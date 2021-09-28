#!/bin/bash

experiment=int
cert=/opt/rucio/etc/proxy
key=/opt/rucio/etc/proxy
host=msg-int-rucio.okd.fnal.gov
topic=/topic/rucio.events.int
durable=False
unsubscribe=False
start_rse=DCACHE_BJWHITE_START
end_rses=DCACHE_BJWHITE_END,DCACHE_BJWHITE_END2
rucio_account=root
debug=False
num_files=1
file_size=1024

python3 ./run_transfer_test.py \
    --experiment ${experiment} \
    --cert ${cert} \
    --key ${key} \
    --host ${host} \
    --topic ${topic} \
    --durable ${durable} \
    --unsubscribe ${unsubscribe} \
    --start_rse ${start_rse} \
    --end_rses ${end_rses} \
    --rucio_account ${rucio_account} \
    --num_files ${num_files} \
    --file_size ${file_size} \
    --debug ${debug}
