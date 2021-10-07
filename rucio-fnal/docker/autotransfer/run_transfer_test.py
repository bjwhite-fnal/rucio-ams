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

class TransferInfo:
    def __init__(self, scope, name, dst_rse, state, request_id):
        self.completed = False
        self.scope = scope
        self.name = name
        self.dst_rse = dst_rse
        self.state = state
        self.request_id = request_id

    def set_complete(self):
        self.completed = True

    def set_state(self, state):
        self.state = state

class RucioListener(stomp.ConnectionListener):
    def __init__(self, conn, scope, topic, sub_id, all_files):
        self.shutdown = False
        self.conn = conn
        self.topic = topic
        self.sub_id = sub_id
        self.scope = scope
        self.all_files = all_files
        self.transfers_by_rse = collections.defaultdict(list)
        self.terminal_states = ['transfer-submission-failed', 'transfer-failed', 'transfer-done']

    def reconnect_and_subscribe(self):
        self.conn.connect(wait=True)
        self.conn.subscribe(self.topic, self.sub_id)

    def on_disconnected(self):
        logger.error(f'Lost connection to broker')
        self.reconnect_and_subscribe()

    def on_error(self, msg):
        logger.error(f'Recieved error frame: {msg}')

    def on_message(self, msg):
        logger.debug(f'Received raw message: {msg}')
        try:
            msg_data = json.loads(msg.body)
        except ValueError:
            logger.error('Unable to decode JSON data')
            return
        self.process_message(msg_data)

    def match_transfer(self, transfer_info, tracked_transfer):
        return bool(
            transfer_info.scope == tracked_transfer.scope and \
            transfer_info.name == tracked_transfer.name and \
            transfer_info.dst_rse == tracked_transfer.dst_rse)

    def tracking(self, transfer_info):
        return bool(
            any(
                self.match_transfer(transfer_info, tracked_transfer) for \
                tracked_transfer in self.transfers_by_rse[transfer_info.dst_rse]))

    def get_tracked_transfer(self, transfer_info):
        for tracked_transfer in self.transfers_by_rse[transfer_info.dst_rse]:
            if self.match_transfer(transfer_info, tracked_transfer):
                logger.info(f'Found tracked transfer for:\n\t\
                        File: {tracked_transfer.name}\n\t\
                        Destination RSE: {tracked_transfer.dst_rse}\n\t\
                        Destination RSE: {tracked_transfer.dst_rse}\n\t\
                        Request ID: {tracked_transfer.request_id}\n\t\
                        Completed: {tracked_transfer.completed}')
                return tracked_transfer

    def process_message(self, msg):
        logger.info(f'Processing received message: {msg}\n')
        event_type = msg['event_type']
        payload = msg['payload']
        transfer_info = None
        if 'transfer' in event_type:
            scope = payload['scope']
            name = payload['name']
            dst_rse = payload['dst-rse']
            if event_type == 'transfer-failed':
                state = 'failed'
            else:
                state = payload['state']
            request_id = payload['request-id']
            transfer_info = TransferInfo(scope, name, dst_rse, state, request_id)

        # Is this a new transfer for that dataset that needs tracked?
        if event_type == 'transfer-queued':
            logger.info('Message is of type transfer-queued')
            assert transfer_info is not None
            correct_scope = bool(transfer_info.scope == self.scope)
            correct_name = bool(transfer_info.name in self.all_files)
            if correct_scope and correct_name:
                logger.info(f'Match for {self.scope}:{transfer_info.name}. Checking if already tracked')
                if not self.tracking(transfer_info):
                    logger.info('Commencing tracking of transfer for {self.scope}:{transfer_info.name} to {transfer_info.dst_rse}')
                    self.transfers_by_rse[transfer_info.dst_rse].append(transfer_info)
                else:
                    logger.info('Transfer of file {self.scope}:{transfer_info.name} is already being tracked. Skipping.')

        # Is this failed transfer one that we are tracking for our test?
        elif event_type in self.terminal_states:
            logger.info(f'Message is of type {event_type}')
            if self.tracking(transfer_info):
                tracked_transfer = self.get_tracked_transfer(transfer_info)
                tracked_transfer.set_state(transfer_info.state)
                logger.info(f'Updated state to {tracked_transfer.state} for transfer:\n\t\
                    {tracked_transfer.request_id} for file {tracked_transfer.name}')
                tracked_transfer.set_complete()
                logger.info(f'Set completion flag {tracked_transfer.completed} for transfer:\n\t\
                    {tracked_transfer.request_id} for file {tracked_transfer.name}')
        logger.info(f'Full list of transfers being tracked:\n\t{self.transfers_by_rse}')

class RucioTransferTest:
    def __init__(self, rucio_account, rucio_scope, data_dir, file_size, start_rse, dst_rses, all_files):
        self.rucio_account = rucio_account
        self.rucio_scope = rucio_scope
        self.data_dir = data_dir
        self.file_size = file_size
        self.start_rse = start_rse
        self.dst_rses = dst_rses
        self.all_files = all_files
        self.listener_thread = None
        self.is_subscribed = threading.Event()
        self.failed = threading.Event()
        self.conn = None
        self.retry_count = 3

    def setup_listener(self, host, port, cert, key, topic, sub_id, vhost, all_files):
        logger.info('Creating the listener thread to monitor the Rucio event stream')
        sub_id = 'placeholder'
        self.listener_thread = threading.Thread(target=self.run_listener, args=(host, port, cert, key, topic,
            sub_id, vhost, all_files))
        self.listener_thread.start()
        return self.listener_thread

    def run_listener(self, host, port, cert, key, topic, sub_id, vhost, all_files):
        logger.info(f'Listener thread starting up.')
        # Setup the connection
        logger.info(f'Creating Connection to\n\t{host}:{port}\n\tCert:{cert}\n\tKey: {key}\n\tTopic: {topic}\n\tSub ID: {sub_id}\n\tvhost: {vhost}')
        self.conn, self.rucio_listener = self.establish_broker_connection(host, port, cert, key, topic, sub_id, vhost, all_files)

        # Process rules
        logger.info(f'The listener will now watch for test transfer datasets...')
        while not self.rucio_listener.shutdown:
            time.sleep(120)
            self.rucio_listener.shutdown = self.check_if_finished()

        # Shut down cleanly
        logger.info('Listener thread completing...')
        self.conn.disconnect()

    def establish_broker_connection(self, host, port, cert, key, topic, sub_id, vhost, all_files):
        conn = stomp.Connection12(
            [(host, port)],
            use_ssl=True,
            ssl_cert_file=cert,
            ssl_key_file=key,
            vhost=vhost
        )
        rucio_listener = RucioListener(conn, self.rucio_scope, topic, sub_id, all_files)
        conn.set_listener('RucioListener', rucio_listener)
        logger.info(f'Listener thread connecting to event stream at: {host}:{port}')
        i = 0
        while i < self.retry_count:
            try:
                conn.connect(wait=True)
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
        conn.subscribe(topic, sub_id)
        logger.info(f'Listener thread successfully subscribed to topic: {topic}')
        self.is_subscribed.set()
        return conn, rucio_listener

    def check_if_finished(self):
        logger.info('Checking if all transfers to all RSEs have been completed.')
        all_file_statuses = []
        # For each file we need to track
        for filename in self.all_files:
            file_rse_statuses = []
            # See if there is a completed transfer for it at each destination rse 
            for dst_rse in self.dst_rses:
                logger.info(f'Checking transfers for file {filename} at RSE: {dst_rse} ')
                if len(self.rucio_listener.transfers_by_rse[dst_rse]) == 0: # all([]) is True
                    logger.info(f'No transfers yet at {dst_rse}')
                    file_rse_statuses.append(False)
                    continue
                rse_transfers = self.rucio_listener.transfers_by_rse[dst_rse]
                logger.info(f'Transfers at RSE {dst_rse}: {rse_transfers}')
                for transfer in self.rucio_listener.transfers_by_rse[dst_rse]:
                    if transfer.completed and transfer.name == filename:
                        logger.info(f'Completed transfer for {filename} at {dst_rse} with request-id: {transfer.request_id}')
                        file_rse_statuses.append(True)
                    else:
                        logger.info(f'Uncompleted transfer for {filename} at {dst_rse} with\n\t\
                            request-id: {transfer.request_id}\n\t\
                            state: {transfer.state}\n\t\
                            completed: {transfer.completed}')
                        file_rse_statuses.append(False)
            all_done_rse = all(file_rse_statuses)
            logger.info(f'File transfer completion statuses for RSE {dst_rse}: {file_rse_statuses}')
            all_file_statuses.append(all_done_rse)
        all_done = all(all_file_statuses)
        logger.info(f'All files transferred: {all_done}')
        return all_done

    def rucio_upload(self, filepath):
        account_arg = '-a {rucio_account}'.format(rucio_account=self.rucio_account)
        rse_arg = '--rse {start_rse}'.format(start_rse=self.start_rse)
        cmd = 'rucio {account_arg} upload {rse_arg} {filepath}'.format(account_arg=account_arg, rse_arg=rse_arg, filepath=filepath)
        logger.info(f'Running command: {cmd}')
        rucio_upload_proc = subprocess.run(cmd, shell=True)
        assert rucio_upload_proc.returncode == 0

    def rucio_create_dataset(self, didfile_path):
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
        return rule_id

def start_listener(tester, host, port, cert, key, topic, sub_id, vhost, all_files):
    # Start the listener thread
    listener_thread = tester.setup_listener(host, port, cert, key, topic, sub_id, vhost, all_files)
    while not tester.is_subscribed.is_set() or tester.failed.is_set():
        if tester.failed.is_set():
            logger.error(f'Failed to connect to the message broker at:')
            logger.error(f'\t{host}:{port}\n\tCert:{cert}\n\tKey: {key}\n\tTopic: {topic}\n\tSub ID: {sub_id}\n\tvhost: {vhost}')
            sys.exit(-1)
        time.sleep(1)
    logger.info(f'Rucio event stream Listener is ready.')
    return listener_thread

def create_file(data_dir, file_size):
    filename = uuid.uuid1()
    abs_filepath = data_dir + '/' + str(filename)
    of = 'of={data_dir}/{filename}'.format(data_dir=data_dir, filename=filename)
    bs = 'bs={file_size}'.format(file_size=file_size)
    filegen_proc = subprocess.run(['dd', 'if=/dev/random',
        of,
        bs,
        'count=1'
    ])
    assert filegen_proc.returncode == 0
    return abs_filepath


def main():
    args = parse_args()
    dest_rses = args.end_rses.split(',')

    # Generate the files that will be transferred
    logger.info(f'Generating {args.num_files}x{args.file_size}byte files')
    os.mkdir(args.data_dir)
    generated_files = []
    for i in range(args.num_files):
        filepath = create_file(args.data_dir, args.file_size)
        generated_files.append(filepath)
    filenames = list(map(os.path.basename, generated_files))
    logger.info(f'Generated {args.num_files} files')

    tester = RucioTransferTest(
        args.rucio_account,
        args.rucio_scope,
        args.data_dir,
        args.file_size,
        args.start_rse,
        dest_rses,
        filenames
    )
    vhost = '/'
    sub_id = 'test'
    logger.info(f'Filenames to listen for: {filenames}')
    listener_thread = start_listener(tester, args.host, args.port, args.cert, args.key, args.topic, sub_id,
            vhost, filenames)


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
    for dest_rse in dest_rses:
        rule_id = tester.rucio_add_rule(dataset_did, dest_rse)
        logger.info(f'Added rule {rule_id} to transfer dataset {dataset_did} from {args.start_rse} to {dest_rse}.')
    
    # Now monitor for the completion of the transfers.
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
    parser.add_argument('--rucio_scope',
        default='user.root',
        help='Rucio scope to use for this test')
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
