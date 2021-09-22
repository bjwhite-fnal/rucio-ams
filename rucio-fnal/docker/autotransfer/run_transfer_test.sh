#!/bin/bash

# This script tests that Rucio is taking file uploads, and transferring files appropriately

# STOMP listener script configuration
listen_event="transfer-done"
experiment=${1:-int}
cert=${2:-/tmp/x509up_u}
key=${3:-/tmp/x509up_u}
topic=${4:-/topic/rucio.events.}
durable=${5:-false}
unsubscribe=${6:-false}
debug=${7:-false}
dry_run=${8:-false}

host=msg-${experiment}-rucio.okd.fnal.gov:443
cert=${cert}$(id -u)
key=${key}$(id -u)
topic=${topic}${experiment}

printf "Listener settings:\n\texperiment: ${experiment}\n\tcert: ${cert}\n\tkey: ${key}\n\ttopic: ${topic}\n\tdurable: ${durable}\n\tunsubscribe: ${unsubscribe}\n\tdebug: ${debug}\n\n"

# Rucio Configuration
start_rse=${9:-DCACHE_BJWHITE_START}
end_rse=${10:-DCACHE_BJWHITE_END}
dataset_name=rucio_transfer_test_$(uuidgen)
rucio_user=root # This should be the experiment production user eventually to get this to run automatically on OKD

printf "Rucio settings:\n\tStart RSE: ${start_rse}\n\tEnd RSE: ${end_rse}\n\tDataset name: ${dataset_name}\n\tRucio user: ${rucio_user}\n\n"

# Settings controlling the number and size of files to generate
data_dir=/tmp/rucio_status_test.$(uuidgen)
START=0
END=0
file_size=1024
num_files="$((END-START+1))"

printf "Data settings:\n\tData directory: ${data_dir}\n\tNum files: ${num_files}\n\n"

if [[ ! $dry_run == true ]]; then
    dry_run=false
fi

if [[ ! $durable == true ]]; then
    durable=True
else
    durable=False
fi

if [[ ! $unsubscribe == true ]]; then
    unsubscribe=True
else
    unsubscribe=False
fi

if [[ ! $debug == true ]]; then
    debug=True
else
    debug=False
fi


printf "Using data dir: ${data_dir}\n"
mkdir ${data_dir}
 
printf "Generating files to be uploaded.\n"
for (( c=$START; c<=$END; c++ ))
do
    name=$(uuidgen)
    if ! dd if=/dev/zero of=$data_dir/$name bs=$file_size count=1 > /dev/null 2>&1; then
        printf "Error during generation of data file: ${?}\n"
        exit 1
    fi
    printf "Files generated\n"
done

# Upload the test files into Rucio
for f in $(ls ${data_dir}); do
    if [[ ${dry_run} == false ]]; then
        printf "Uploading ${data_dir}/${f} to ${start_rse}\n"
        if ! rucio -a ${rucio_user} upload --rse $start_rse $data_dir/$f; then
            exit 1
        fi
        printf "Uploaded test files to ${start_rse} RSE.\n"
    fi
done

# Add a dataset for the files
# First create DID file
for f in $(ls $data_dir); do
    printf "Adding DID to: ${data_dir}/tmdids\n"
    echo "user.${rucio_user}:${f}" >> ${data_dir}/tmpdids
done

if [[ ${dry_run} == false ]]; then
    printf "Creating dataset ${dataset_name} and adding files\n"
    rucio add-dataset user.${rucio_user}:${dataset_name}
    if ! rucio -a ${rucio_user} attach user.${rucio_user}:${dataset_name} -f ${data_dir}/tmpdids; then
        exit 1
    fi
fi

# Add rule to move the dataset from $start_rse to $end_rse
if [[ ${dry_run} == false ]]; then
    printf "Making a rule to start the transfer of user.${rucio_user}:${dataset_name} from ${start_rse} -> ${end_rse}\n"
    if ! rucio -a ${rucio_user} add-rule user.${rucio_user}:${dataset_name} 1 ${end_rse}; then
        exit 1
    fi
fi

all_done=0
# Subscribe to the STOMP broker and wait for notifiations that the transfers have been completed
if [[ ${dry_run} == false ]]; then
    python listen_for_event.py ${host} \
        --listen-event ${listen_event} \
        --cert ${cert} \
        --key ${key} \
        --topic ${topic} \
        #--durable ${durable} \
        #--unsubscribe ${unsubscribe} \
        #--debug ${debug}
fi



all_done=1
if [ $all_done == 1 ]; then
    rm -r $data_dir
fi
