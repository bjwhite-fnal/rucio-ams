# Generate files, send them to RSEs, and monitor transfers for completion
# Brandon White, FNAL, 2021

import argparse
import collections
import json
import logging
import os
import queue
import random
import ssl
import stomp
import subprocess
import sys
import threading
import time
import uuid

from rucio.client import Client as RucioClient
from rucio.client.uploadclient import UploadClient as RucioUploadClient

DEFAULT_PORT = 443 # Note that FNAL OKD Rucio STOMP brokers are on 443
DEFAULT_CHECK_TIME = 120
DEFAULT_NUM_FILES = 1
DEFAULT_FILE_SIZE = 1024
DEFAULT_TRANSFER_TIMEOUT = 600
DEFAULT_RULE_LIFETIME = 10000

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
        logger.info(f'Reconnecting to the message broker @ topic: {self.topic} and subscription id: {self.sub_id}')
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
        logger.info(f'Processing received {msg["event_type"]} message.')
        event_type = msg['event_type']
        payload = msg['payload']
        transfer_info = None
        if 'transfer' in event_type:
            scope = payload['scope']
            name = payload['name']
            dst_rse = payload['dst-rse']
            if event_type == 'transfer-failed':
                state = 'failed'
            elif event_type == 'transfer-done':
                state = 'done'
            else:
                state = payload['state']
            request_id = payload['request-id']
            transfer_info = TransferInfo(scope, name, dst_rse, state, request_id)

        # Is this a new transfer for that dataset that needs tracked?
        if event_type == 'transfer-queued':
            logger.info('Processing event: transfer-queued')
            assert transfer_info is not None
            correct_scope = bool(transfer_info.scope == self.scope)
            correct_name = bool(transfer_info.name in self.all_files)
            if correct_scope and correct_name:
                logger.info(f'Match for {self.scope}:{transfer_info.name}. Checking if already tracked')
                if not self.tracking(transfer_info):
                    logger.info(f'Commencing tracking of transfer for {self.scope}:{transfer_info.name} to {transfer_info.dst_rse}')
                    self.transfers_by_rse[transfer_info.dst_rse].append(transfer_info)
                else:
                    logger.info(f'Transfer of file {self.scope}:{transfer_info.name} is already being tracked. Skipping.')

        # Is this failed transfer one that we are tracking for our test?
        elif event_type in self.terminal_states:
            logger.info(f'Processing event: {event_type}')
            if self.tracking(transfer_info):
                tracked_transfer = self.get_tracked_transfer(transfer_info)
                tracked_transfer.set_state(transfer_info.state)
                logger.info(f'Updated state to {tracked_transfer.state} for transfer:\n\t\
                    {tracked_transfer.request_id} for file {tracked_transfer.name}')
                tracked_transfer.set_complete()
                logger.info(f'Set completion flag {tracked_transfer.completed} for transfer:\n\t\
                    {tracked_transfer.request_id} for file {tracked_transfer.name}')
            else:
                logger.debug('Skipping... Not for our files.')
        logger.debug(f'Full list of transfers being tracked:\n\t{self.transfers_by_rse}')


class TransferTestParams:
    def __init__(self, rucio_account, rucio_scope, start_rse, dst_rses, check_time, transfer_timeout, lifetime):
        # Data and Rucio Parameters
        self.rucio_account = rucio_account
        self.rucio_scope = rucio_scope
        self.start_rse = start_rse
        self.dst_rses = dst_rses
        self.transfer_timeout = transfer_timeout
        self.lifetime = lifetime
        self.broker_retry_count = 3
        self.check_time = check_time


class RucioTransferTest:
    def __init__(self, test_params):
        self.test_params = test_params
        self.rucio_client = RucioClient(account=self.test_params.rucio_account)
        self.rucio_upload_client = RucioUploadClient(_client=self.rucio_client, logger=logger)
        self.all_files = []
        self.listener_thread = None
        self.conn = None
        self.is_subscribed = threading.Event()
        self.failed = threading.Event()

    def setup_listener(self, host, port, cert, key, topic, sub_id, vhost):
        logger.info('Creating the listener thread to monitor the Rucio event stream')
        sub_id = 'placeholder'
        self.listener_thread = threading.Thread(
            target=self.run_listener,
            args=(host, port, cert, key, topic, sub_id, vhost, self.all_files))
        self.listener_thread.start()
        return self.listener_thread

    def run_listener(self, host, port, cert, key, topic, sub_id, vhost, files_to_track):
        logger.info(f'Listener thread starting up.')
        # Setup the connection
        logger.info(f'Creating Connection to\n\t{host}:{port}\n\tCert:{cert}\n\tKey: {key}\n\tTopic: {topic}\n\tSub ID: {sub_id}\n\tvhost: {vhost}')
        try:
            self.conn, self.rucio_listener = self.establish_broker_connection(host, port, cert, key, topic, sub_id, vhost, files_to_track)
        except TypeError:
            logger.info('Unable to connect to broker. Failing test.')
        else:
            # Process rules
            logger.info(f'The listener will now watch for test transfer datasets...')
            while not self.rucio_listener.shutdown:
                time.sleep(self.test_params.check_time)
                self.rucio_listener.shutdown = self.check_if_finished(files_to_track)

            # Print information about the transfers
            self.print_statistics()

            # Shut down cleanly
            logger.info('Listener thread completing...')
            self.conn.disconnect()

    def print_statistics(self):
        good_transfers = []
        bad_transfers = []
        good_rses = []
        bad_rses = []
        for rse in self.test_params.dst_rses:
            transfers = self.rucio_listener.transfers_by_rse[rse]
            for transfer in transfers:
                if transfer.state == 'done':
                    good_transfers.append(transfer)
                    good_rses.append(transfer.dst_rse)
                else:
                    bad_transfers.append(transfer)
                    bad_rses.append(transfer.dst_rse)
        logger.info(f'There were { len(good_transfers) } successful transfers and { len(bad_transfers) } transfers that failed')
        logger.info(f'Good RSEs: {good_rses}')
        logger.info(f'Bad RSEs: {bad_rses}')

    def establish_broker_connection(self, host, port, cert, key, topic, sub_id, vhost, files_to_track):
        conn = stomp.Connection12(
            [(host, port)],
            reconnect_attempts_max=1,
            vhost=vhost,
            heartbeats=(20000,20000)
        )
        logger.info(f'Listener thread created connection object to: {host}:{port}')
        conn.set_ssl(
            for_hosts=[(host, port)],
                cert_file=cert,
                key_file=key,
                ssl_version=ssl.PROTOCOL_TLSv1_2
        )
        logger.info(f'Listener thread configured SSL connection to: {host}:{port}. Cert: "{cert}" Key: "{key}"')
        rucio_listener = RucioListener(conn, self.test_params.rucio_scope, topic, sub_id, files_to_track)
        conn.set_listener('RucioListener', rucio_listener)
        logger.info(f'Listener thread connecting to event stream at: {host}:{port}')
        i = 0
        while i < self.test_params.broker_retry_count:
            try:
                conn.connect(wait=True)
            except stomp.exception.ConnectFailedException as ex:
                if i == self.test_params.broker_retry_count-1:
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

    def check_if_finished(self, files_to_track):
        logger.info('Checking if all transfers to all RSEs have been completed.')
        all_file_statuses = []
        # For each file we need to track
        for filename in files_to_track:
            file_rse_statuses = []
            # See if there is a completed transfer for it at each destination rse 
            for dst_rse in self.test_params.dst_rses:
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


    def prepare_items(self, generated_files, dataset_name=None):
        # TODO: Create the dataset before hand, and upload files directly into it
        items = []
        for f in generated_files:
            self.all_files.append(os.path.basename(f)) # Keep track of the filenames, the listener needs to know them
            item = {
                'path': f,
                'rse': self.test_params.start_rse,
                'did_scope': self.test_params.rucio_scope,
                'dataset_scope': self.test_params.rucio_scope,
                #'dataset_name':,
                'register_after_upload': True, # I really can't think of a good reason to ever turn this off
                'lifetime': self.test_params.lifetime,
                'transfer_timeout': self.test_params.transfer_timeout,
            }
            items.append(item)
        return items


    def rucio_create_dataset(self, items):
        logger.info(f'Creating Rucio dataset')
        dids = []
        for item in items:
            did = { 
                'scope' : os.path.basename(item['did_scope']),
                'name' : os.path.basename(item['path'])
            }
            dids.append(did)
        dataset_name = str(uuid.uuid1())
        logger.info(f'Gathered {len(dids)} files to attach to dataset {dataset_name}')

        rc = self.rucio_client.add_dataset(
                self.test_params.rucio_scope,
                dataset_name,
                #statues,
                #meta,
                #rules, # TODO: Use to specify replication rules at dataset creation time
                lifetime=self.test_params.lifetime,
                files=dids, # replaces didfile_path list of dids to attach to the dataset
                rse=self.test_params.start_rse
        )
        return f'{self.test_params.rucio_scope}:{dataset_name}'


    def rucio_add_rule(self, dataset_did, dest_rse, num_copies=1):
        # TODO: Refactor to use the Python client properly

        account_arg = '-a {rucio_account}'.format(rucio_account=self.test_params.rucio_account)
        cmd = 'rucio {account_arg} add-rule {dataset_did} {num_copies} {dest_rse}'\
            .format(account_arg=account_arg, dataset_did=dataset_did, num_copies=num_copies, dest_rse=dest_rse)
        logger.info(f'Running command: {cmd}')
        rucio_add_rule_proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        assert rucio_add_rule_proc.returncode == 0
        rule_id = rucio_add_rule_proc.stdout.strip().decode('utf-8')
        return rule_id


def start_listener(tester, host, port, cert, key, topic, sub_id, vhost):
    # Start the listener thread
    listener_thread = tester.setup_listener(host, port, cert, key, topic, sub_id, vhost)
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
    if args.debug:
        logger.setLevel(logging.DEBUG)
    logger.info(f'Arguments to Rucio test: {args}')
    dest_rses = args.end_rses.split(',')

    # Generate the files that will be transferred
    logger.info(f'Generating files {args.num_files}x{args.file_size} bytes in size.')
    os.mkdir(args.data_dir)
    generated_files = []
    for i in range(args.num_files):
        filepath = create_file(args.data_dir, args.file_size)
        generated_files.append(filepath)
    logger.info(f'Generated {args.num_files} files')


    test_params =  TransferTestParams(
        args.rucio_account,
        args.rucio_scope,
        args.start_rse,
        dest_rses,
        args.check_time,
        args.transfer_timeout,
        args.lifetime)
    tester = RucioTransferTest(test_params)

    # Prepare the files by turning them into `items` for rucio.client.uploadclient.upload()
    logger.info(f'Preparing {len(generated_files)} files')
    items = tester.prepare_items(generated_files)
    logger.info(f'Preparing {len(items)} files for Rucio upload to {tester.test_params.start_rse}')


    vhost = '/'
    sub_id = 'test'
    logger.info(f'Filenames to listen for: {tester.all_files}')
    listener_thread = start_listener(tester, args.host, args.port, args.cert, args.key, args.topic, sub_id, vhost)

    # Upload the test files to Rucio
    logger.info(f'Uploading {len(generated_files)} files')
    rc = tester.rucio_upload_client.upload(items)
    assert rc == 0
    logger.info(f'Uploaded {len(generated_files)} files')

    # Create the Rucio dataset and attach the associated files
    dataset_did = tester.rucio_create_dataset(items)
    logger.info(f'Created Rucio dataset {dataset_did}')

    # Create a rule for the dataset on each of the destination RSEs
    for dest_rse in dest_rses:
        rule_id = tester.rucio_add_rule(dataset_did, dest_rse)
        logger.info(f'Added rule {rule_id} to transfer dataset {dataset_did} from {args.start_rse} to {dest_rse}.')
    
    # Now monitor for the completion of the transfers.
    listener_thread.join()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--experiment',
        help = 'Name of the experiment this transfer test will be run for')
    parser.add_argument('--cert',
        default = os.environ.get('BROKER_CERT', '/opt/certs/hostcert.pem'),
        help = 'PEM certificate for BROKER authentication (NO VOMS ATTRIBUTES)')
    parser.add_argument('--key',
        default = os.environ.get('BROKER_KEY', '/opt/certs/hostkey.pem'),
        help = 'PEM key for BROKER authentication (NO VOMS ATTRIBUTES)')
    parser.add_argument('--host',
        help = 'Rucio message broker to connect to in order to listen to the event stream.')
    parser.add_argument('--port',
        type = int,
        default = DEFAULT_PORT,
        help = 'Rucio message broker to connect to in order to listen to the event stream.')
    parser.add_argument('--topic',
        help = 'Message topic to connect to.')
    parser.add_argument('--durable',
        help = '')
    parser.add_argument('--unsubscribe',
        help = '')
    # TODO: Change to use --source_rse_expression instead
    parser.add_argument('--start_rse',
        help = 'Rucio RSE to upload transfer files to.')
    # TODO: Change to use --dest_rse_expression instead
    parser.add_argument('--end_rses',
        help = 'Comma-separated list of RSEs that the generated transfer files will be have rules created for.')
    parser.add_argument('--rucio_account',
        default='root',
        help = 'User that Rucio commands will be run as')
    parser.add_argument('--rucio_scope',
        default='user.root',
        help = 'Rucio scope to use for this test')
    parser.add_argument('--num_files',
        default = DEFAULT_NUM_FILES,
        type = int,
        help = 'Number of files that will be generated the rules to transfer. Default: {DEFAULT_NUM_FILES}')
    parser.add_argument('--file_size',
        default = DEFAULT_FILE_SIZE,
        type = int,
        help = 'Size of each generated test transfer file')
    parser.add_argument('--data_dir',
        default = '/tmp/%s' % str(uuid.uuid1()),
        help = 'Where to store the temporary data generated for this test.')
    parser.add_argument('--debug',
        help = 'Enable debug level logging.')
    parser.add_argument('--check_time',
        default=DEFAULT_CHECK_TIME,
        type = int,
        help = 'How often to check through all the transfers to see if they are done. Default: 120s')
    parser.add_argument('--transfer_timeout',
        default = DEFAULT_TRANSFER_TIMEOUT,
        type = int,
        help = f'How long to wait before Rucio uploads to the initial RSE timeout. Default: {DEFAULT_TRANSFER_TIMEOUT}')
    parser.add_argument('--lifetime',
        default=DEFAULT_RULE_LIFETIME,
        type = int,
        help = f'How long before Rucio locks on the test files expire. Default: {DEFAULT_RULE_LIFETIME}')
    parser.add_argument('--activity',
        help = 'The transfer activity to be passed to Rucio.')
    return parser.parse_args()

if __name__ == '__main__':
    main()
