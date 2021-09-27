import sys
import os
import argparse
import uuid
import random
import subprocess
import logging

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--experiment',
        help='Name of the experiment this transfer test will be run for')
    parser.add_argument('--cert',
        help='PEM certificate for Rucio authentication')
    parser.add_argument('--key',
        help='PEM key for Rucio authentication')
    parser.add_argument('--host',
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
    parser.add_argument('--rucio_user',
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
        default = '/tmp/transfertest/%s' % str(uuid.uuid1()),
        help='Where to store the temporary data generated for this test.')
    parser.add_argument('--debug',
        help='Enable debug level logging.')
    return parser.parse_args()

def create_file(data_dir, file_size):
    filename = uuid.uuid1()
    abs_filepath = data_dir + '/' + str(filename)
    of = 'of={data_dir}/{filename}'
    bs = 'bs={file_size}'
    filegen_proc = subprocess.run(['dd', 'if=/dev/random',
        of.format(data_dir=data_dir, filename=filename),
        bs.format(file_size=file_size), 'count=1'
    ])
    assert filegen_proc.returncode == 0
    return abs_filepath

def rucio_upload(rucio_account, filepath):
    account_arg = '-a {rucio_account}'
    
    rucio_upload_proc = subprocess.run(['rucio', 
        account_arg.format(rucio_account=rucio_account),
        'upload',
        start_rse,
        filepath
    ])
    assert rucio_upload_proc.returncode == 0

def rucio_create_dataset(did_filepath, rucio_account, dataset_name=None):
    if not dataset_name:
        dataset_name = str(uuid.uuid1())
    account_arg = '-a {rucio_account}'
    dataset_did = 'user.{rucio_account}:{dataset_name}'
    rucio_create_ds_proc = subprocess.run(['rucio', 
        account_arg.format(rucio_account=rucio_account),
        'add-dataset',
        dataset_did.format(rucio_account=rucio_account, dataset_name=dataset_name)
    ])
    assert rucio_create_ds_proc.returncode == 0
    return dataset_did

def rucio_attach_dataset(rucio_account, dataset_did, did_filepath):
    account_arg = '-a {rucio_account}'
    with open(did_filepath) as df:
        for did in df:
            rucio_create_ds_proc = subprocess.run(['rucio', 
                account_arg.format(rucio_account=rucio_account),
                'attach',
                dataset_did.format(rucio_account=rucio_account, dataset_name=dataset_name)
            ])
            

def main(): 
    args = parse_args()

    # Generate the files that will be transferred
    os.mkdir(args.data_dir)
    generated_files = []
    for i in range(args.num_files):
        filepath = create_file(args.data_dir, args.file_size)
        generated_files.append(filepath)

    # Upload the test files to Rucio
    for f in generated_files:
        rucio_upload(args.rucio_account, f)

    # Create the DID file for specification of dataset files later
    did_filepath = args.data_dir + '/' + 'didfile'
    with open(did_filepath) as df:
        for f in generated_files:
            did = 'user.{rucio_user}:{filename}\n'.format(rucio_user=args.rucio_user, filename=os.path.basename(f))
            df.write(did)

    # Create the Rucio dataset for these files
    dataset_did = rucio_create_dataset(did_filepath, args.rucio_account)
    # Attach each of the files to the dataset
    rucio_attach_dataset(args.rucio_account, dataset_did, did_filepath)
        
        

if __name__ == '__main__':
    main()
