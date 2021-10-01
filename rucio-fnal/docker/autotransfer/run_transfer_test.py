import sys
import os
import argparse
import uuid
import random
import subprocess
import logging
import threading
import stomp
import time
import queue
import collections
import json

logging.basicConfig(format='%(asctime)-15s %(name)s %(levelname)s %(message)s', level=logging.INFO)
logging.getLogger('stomp.py').setLevel(logging.WARNING)
logger = logging.getLogger('transfer_test')

class RucioListener(stomp.ConnectionListener):
    def __init__(self, conn, topic, sub_id):
        self.conn = conn
        self.topic = topic
        self.sub_id = sub_id
        self.shutdown = False
        self.rule_transfers = collections.defaultdict(list)

    def reconnect_and_subscribe(self):
        self.conn.connect(wait=True)
        self.conn.subscribe(self.topic, self.sub_id)

    def on_disconnected(self):
        logger.error(f'Lost connection to broker')
        self.reconnect_and_subscribe()

    def on_error(self, msg):
        logger.error(f'Recieved error frame: {msg}')

    def on_message(self, msg):
        logger.info(f'Received raw message: {msg}')
        try:
            msg_data = json.loads(msg.body)
        except ValueError:
            logger.error('Unable to decode JSON data')
            return

        # Need to map transfers to rules
        self.process_message(msg_data)

    def process_message(self, msg):
        event_type = msg['event_type']
        logger.info(f'Successfully received message: {msg}\n')

        if event_type == 'transfer-queued':
            rule_id = msg['payload']['rule-id']
            request_id = msg['payload']['request-id']
            request_tracker = [ request_id, False ]
            self.rule_transfers[rule_id].append(request_tracker)
            logger.info(f'Tracking rule {rule_id} request {request_id}')
        elif event_type == 'transfer-done':
            request_id = msg['payload']['request-id']
            rule_ids = self.update_request_status(request_id)
            logger.info(f'Request {request_id} completed for rule {rule_ids}')
        elif event_type == 'transfer-submission-failed':
            request_id = msg['payload']['request-id']
            rule_ids = self.update_request_status(request_id)
            request_state = msg['payload']['state']
            logger.info(f'Request {request_id} (STATE: {request_state}) failed for rule {rule_ids}')
        else:
            #logger.info(msg)
            pass
        if self.check_if_finished():
            self.shutdown = True

    def update_request_status(self, request_id):
        for rule in self.rule_transfers:
            transfers = self.rule_transfers[rule]
            try:
                idx = transfers.index(request_id)
            except ValueError:
                pass
            else:
                self.rule_transfers[rule][idx][1] = True

    def check_if_finished(self):
        rules_done = { (rule, False) for rule in self.rule_transfers.keys() }
        for rule in self.rule_transfers: # Check if all transfers for a rule are complete
            transfers = self.rule_transfers[rule]
            rule_done = all( [ transfer_status[1] == True for transfer_status in transfers ] )
            if rule_done:
                rules_done[rule] = True
        all_done = all( transfer_status == True for transfer_status in self.rule_transfers.values() ) #  Check that all rules are done
        return all_done

class RucioTransferTest:
    def __init__(self, rucio_account, data_dir, file_size, start_rse):
        self.rucio_account = rucio_account
        self.data_dir = data_dir
        self.file_size = file_size
        self.start_rse = start_rse
        self.listener_thread = None
        self.is_subscribed = threading.Event()
        self.wait_for_rules = threading.Event()
        self.failed = threading.Event()
        self.rules_to_monitor = []
        self.conn = None
        self.retry_count = 3

    def setup_listener(self, host, port, cert, key, topic, sub_id, vhost):
        logger.info('Creating the listener thread to monitor the Rucio event stream')
        sub_id = 'placeholder'
        self.listener_thread = threading.Thread(target=self.run_listener, args=(host, port, cert, key, topic, sub_id, vhost))
        self.listener_thread.start()
        return self.listener_thread

    def run_listener(self, host, port, cert, key, topic, sub_id, vhost):
        logger.info(f'''Listener thread starting up.\nCreating Connection to\n\t{host}:{port}\n\tCert: {cert}\n\tKey: {key}\n\tTopic: {topic}\n\tSub ID: {sub_id}\n\tvhost: {vhost}''')
        self.conn = stomp.Connection12(
            [(host, port)],
            use_ssl=True,
            ssl_cert_file=cert,
            ssl_key_file=key,
            vhost=vhost
        )
        rucio_listener = RucioListener(self.conn, topic, sub_id)
        self.conn.set_listener('RucioListener', rucio_listener)
        logger.info(f'Listener thread connecting to event stream at: {host}:{port}')
        i = 0
        while i < self.retry_count:
            try:
                self.conn.connect(wait=True)
            except stomp.exception.ConnectFailedException as ex:
                if i == self.retry_count-1:
                    logger.error('Listener thread failed to connect.')
                    self.failed.set()
                    return
                time.sleep(1)
                i += 1
            else:
                break
        logger.info(f'Listener thread successfully connected to event stream at: {host}:{port}')
        self.conn.subscribe(topic, sub_id)
        logger.info(f'Listener thread successfully subscribed to topic: {topic}')
        self.is_subscribed.set()
        self.wait_for_rules.wait()
        # Process rules
        logger.info(f'The listener will monitor for the completion of transfers for rules:\n\t{self.rules_to_monitor}')

        while not rucio_listener.shutdown:
            time.sleep(1)

        logger.info('Listener thread completing...')
        self.conn.disconnect()

    def create_file(self):
        filename = uuid.uuid1()
        abs_filepath = self.data_dir + '/' + str(filename)
        of = 'of={data_dir}/{filename}'.format(data_dir=self.data_dir, filename=filename)
        bs = 'bs={file_size}'.format(file_size=self.file_size)
        filegen_proc = subprocess.run(['dd', 'if=/dev/random',
            of,
            bs,
            'count=1'
        ])
        assert filegen_proc.returncode == 0
        return abs_filepath

    def rucio_upload(self, filepath):
        account_arg = '-a {rucio_account}'.format(rucio_account=self.rucio_account)
        rse_arg = '--rse {start_rse}'.format(start_rse=self.start_rse)
        cmd = 'rucio {account_arg} upload {rse_arg} {filepath}'.format(account_arg=account_arg, rse_arg=rse_arg, filepath=filepath)
        logger.info(f'Running command: {cmd}')
        rucio_upload_proc = subprocess.run(cmd, shell=True)
        assert rucio_upload_proc.returncode == 0

    def rucio_create_dataset(self, didfile_path, dataset_name=None):
        if not dataset_name:
            dataset_name = str(uuid.uuid1())
        account_arg = '-a {rucio_account}'.format(rucio_account=self.rucio_account)
        dataset_did = 'user.{rucio_account}:{dataset_name}'.format(rucio_account=self.rucio_account, dataset_name=dataset_name)
        cmd = 'rucio {account_arg} add-dataset {dataset_did}'.format(account_arg=account_arg, dataset_did=dataset_did)
        logger.info(f'Running command: {cmd}')
        rucio_create_ds_proc = subprocess.run(cmd, shell=True)
        assert rucio_create_ds_proc.returncode == 0
        return dataset_did

    def rucio_attach_dataset(self, dataset_did, didfile_path):
        account_arg = '-a {rucio_account}'.format(rucio_account=self.rucio_account)
        didfile_arg = '-f {didfile_path}'.format(didfile_path=didfile_path)
        cmd = 'rucio {account_arg} attach {dataset_did} {didfile_arg}'.format(account_arg=account_arg, dataset_did=dataset_did, didfile_arg=didfile_arg)
        logger.info(f'Running command: {cmd}')
        rucio_attach_ds_proc = subprocess.run(cmd, shell=True)
        assert rucio_attach_ds_proc.returncode == 0

    def rucio_add_rule(self, dataset_did, dest_rse, num_copies=1):
        account_arg = '-a {rucio_account}'.format(rucio_account=self.rucio_account)
        cmd = 'rucio {account_arg} add-rule {dataset_did} {num_copies} {dest_rse}'.format(
            account_arg=account_arg, dataset_did=dataset_did, num_copies=num_copies, dest_rse=dest_rse)
        logger.info(f'Running command: {cmd}')
        rucio_add_rule_proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        assert rucio_add_rule_proc.returncode == 0
        rule_id = rucio_add_rule_proc.stdout.strip().decode('utf-8')
        self.rules_to_monitor.append(rule_id)
        return rule_id

        
def main(): 
    args = parse_args()

    tester = RucioTransferTest(
        args.rucio_account,
        args.data_dir,
        args.file_size,
        args.start_rse
    )
    # Start the listener thread
    vhost = '/'
    sub_id = 'test'
    listener_thread = tester.setup_listener(args.host, args.port, args.cert, args.key, args.topic, sub_id, vhost)
    while not tester.is_subscribed.is_set() or tester.failed.is_set():
        if tester.failed.is_set():
            logger.error(f'''Failed to connect to the message broker at:\n\t{args.host}:{args.port}\n\tCert:{args.cert}\n\tKey: {args.key}\n\tTopic: {args.topic}\n\tSub ID: {sub_id}\n\tvhost: {vhost}''')
            sys.exit(-1)
        time.sleep(1)
    logger.info(f'Rucio event stream Listener is ready.')

    # Generate the files that will be transferred
    logger.info(f'Generating {args.num_files}x{args.file_size}byte files')
    os.mkdir(args.data_dir)
    generated_files = []
    for i in range(args.num_files):
        filepath = tester.create_file()
        generated_files.append(filepath)
    logger.info(f'Generated {args.num_files} files')

    # Upload the test files to Rucio
    logger.info(f'Uploading {len(generated_files)} files')
    for f in generated_files:
        logger.info(f'Uploading: {f}')
        tester.rucio_upload(f)
    logger.info(f'Uploaded {len(generated_files)} files')

    # Create the DID file for specification of dataset files later
    logger.info('Creating the didfile')
    didfile_path = args.data_dir + '/' + 'didfile'
    with open(didfile_path, 'a') as df:
        for f in generated_files:
            did = 'user.{rucio_account}:{filename}\n'.format(rucio_account=args.rucio_account, filename=os.path.basename(f))
            df.write(did)
    logger.info('Created the didfile')

    # Create the Rucio dataset for these files
    dataset_did = tester.rucio_create_dataset(didfile_path)
    logger.info(f'Created Rucio dataset {dataset_did}')

    # Attach the generated files to the dataset via the didfile
    tester.rucio_attach_dataset(dataset_did, didfile_path)
    logger.info(f'Attached files in didfile to dataset {dataset_did}')

    # Create a rule for the dataset on each of the destination RSEs
    end_rses = args.end_rses.split(',')
    for dest_rse in end_rses:
        rule_id = tester.rucio_add_rule(dataset_did, dest_rse)
        logger.info(f'Added rule {rule_id} to transfer dataset {dataset_did} from {args.start_rse} to {dest_rse}.')
    tester.wait_for_rules.set()
    

    # Now monitor for the completion of the transfers.
    logger.info(f'Commencing monitoring of transfer completion for {len(tester.rules_to_monitor)} rules:\n\t{tester.rules_to_monitor}')
    listener_thread.join()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--experiment',
        help='Name of the experiment this transfer test will be run for')
    parser.add_argument('--cert',
        default=os.environ.get('X509_USER_PROXY', '/opt/rucio/etc/proxy'),
        help='PEM certificate for Rucio authentication')
    parser.add_argument('--key',
        default=os.environ.get('X509_USER_PROXY', '/opt/rucio/etc/proxy'),
        help='PEM key for Rucio authentication')
    parser.add_argument('--host',
        help='Rucio message broker to connect to in order to listen to the event stream.')
    parser.add_argument('--port',
        type=int,
        default=443, # Note that FNAL OKD Rucio STOMP brokers are on 443
        help='Rucio message broker to connect to in order to listen to the event stream.')
    parser.add_argument('--topic',
        help='Message topic to connect to.')
    parser.add_argument('--durable',
        help='')
    parser.add_argument('--unsubscribe',
        help='')
    parser.add_argument('--start_rse',
        help='Rucio RSE to upload transfer files to.')
    parser.add_argument('--end_rses',
        help='Comma-separated list of RSEs that the generated transfer files will be have rules created for.')
    parser.add_argument('--rucio_account',
        default='root',
        help='User that Rucio commands will be run as')
    parser.add_argument('--num_files',
        default = 1,
        type=int,
        help='Number of files that will be generated the rules to transfer.')
    parser.add_argument('--file_size',
        default = 1024,
        type=int,
        help='Size of each generated test transfer file')
    parser.add_argument('--data_dir',
        default = '/tmp/%s' % str(uuid.uuid1()),
        help='Where to store the temporary data generated for this test.')
    parser.add_argument('--debug',
        help='Enable debug level logging.')
    return parser.parse_args()

if __name__ == '__main__':
    main()
