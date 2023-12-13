#!/bin/bash

FTS_SERVERS=https://fts3-public.fnal.gov:8446

### ADD USERS ###
# Brandon White
rucio-admin -a root account add bjwhite
rucio-admin -a root identity add --account bjwhite --type X509 --email 'bjwhite@fnal.gov' --id '/DC=org/DC=cilogon/C=US/O=Fermi National Accelerator Laboratory/OU=People/CN=Brandon White/CN=UID:bjwhite'
rucio-admin -a root account add-attribute --key admin --value True bjwhite

# Dennis Lee
user=dylee
rucio-admin -a root account add ${user}
rucio-admin -a root identity add --account ${user} --type X509 --email 'dylee@fnal.gov' --id '/DC=org/DC=cilogon/C=US/O=Fermi National Accelerator Laboratory/OU=People/CN=Dennis Lee/CN=UID:dylee'
rucio-admin -a root account add-attribute --key admin --value True ${user}

# Yuyi Guo
user=yuyi
rucio-admin -a root account add ${user}
rucio-admin -a root identity add --account ${user} --type X509 --email 'yuyi@fnal.gov' --id '/DC=org/DC=cilogon/C=US/O=Fermi National Accelerator Laboratory/OU=People/CN=Yuyi Guo/CN=UID:yuyi'
rucio-admin -a root account add-attribute --key admin --value True ${user}

# Marc Mengel
user=mengel
rucio-admin -a root account add ${user}
rucio-admin -a root identity add --account ${user} --type X509 --email 'mengel@fnal.gov' --id '/DC=org/DC=cilogon/C=US/O=Fermi National Accelerator Laboratory/OU=People/CN=Marc Mengel/CN=UID:mengel'
rucio-admin -a root account add-attribute --key admin --value True ${user}

# Alison Peisker
user=apeisker
rucio-admin -a root account add ${user}
rucio-admin -a root identity add --account ${user} --type X509 --email 'apeisker@fnal.gov' --id '/DC=org/DC=cilogon/C=US/O=Fermi National Accelerator Laboratory/OU=People/CN=Alison Peisker/CN=UID:apeisker'
rucio-admin -a root account add-attribute --key admin --value True ${user}

# Data Dispatcher
user=data_dispatcher
rucio-admin -a root account add ${user}
rucio-admin -a root identity add --account ${user} --type X509 --email 'ivm@fnal.gov' --id '/DC=org/DC=cilogon/C=US/O=Fermi National Accelerator Laboratory/OU=People/CN=Igor Mandrichenko/CN=UID:ivm'
rucio-admin -a root account add-attribute --key admin --value True ${user}

# Igor Mandrichenko
user=ivm
rucio-admin -a root account add ${user}
rucio-admin -a root identity add --account ${user} --type X509 --email 'ivm@fnal.gov' --id '/DC=org/DC=cilogon/C=US/O=Fermi National Accelerator Laboratory/OU=People/CN=Igor Mandrichenko/CN=UID:ivm'
rucio-admin -a root account add-attribute --key admin --value True ${user}

# Lucas Trestka
user=ltrestka
rucio-admin -a root account add ${user}
rucio-admin -a root identity add --account ${user} --type X509 --email 'ltrestka@fnal.gov' --id '/DC=org/DC=cilogon/C=US/O=Fermi National Accelerator Laboratory/OU=People/CN=Lucas Trestka/CN=UID:ltrestka'
rucio-admin -a root account add-attribute --key admin --value True ${user}

# Automatix
user=automatix
rucio-admin -a root account add ${user}
rucio-admin -a root identity add --account ${user} --type X509 --email 'bjwhite@fnal.gov' --id '/DC=org/DC=incommon/C=US/ST=Illinois/O=Fermi Research Alliance/CN=hypot-rucio.fnal.gov'
rucio-admin -a root account add-attribute --key admin --value True ${user}

### ADD RSES ####
rse=FNAL_DCACHE_DISK_TEST
rucio-admin -a root rse add ${rse}
rucio-admin -a root rse set-attribute --rse ${rse} --key fts --value ${FTS_SERVERS}
rucio-admin -a root rse set-attribute --rse ${rse} --key greedyDeletion --value True
rucio-admin -a root rse add-protocol --scheme davs --hostname fndcadoor.fnal.gov --port 2880 --prefix '/pnfs/fnal.gov/usr/hypot/rucio' --domain-json '{"lan": {"read": 1, "write": 1, "delete": 1}, "wan": {"read": 2, "write": 2, "delete": 2, "third_party_copy_read": 2, "third_party_copy_write": 2}}' ${rse}

### ADD DISTANCES ###
#rucio-admin -a root rse add-distance --distance 3 FNAL_DCACHE_DISK_TEST <DESTINATION>
#rucio-admin -a root rse add-distance --distance 3 <DESTINATION> FNAL_DCACHE_DISK_TEST

### ADD Automatix Subscription ###
rucio-admin -a root scope add --scope user.automatix --account automatix
