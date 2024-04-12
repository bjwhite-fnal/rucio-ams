#!/usr/bin/env python3
"""
Script to sync FERRY users to Rucio based on vo/afffiliation

Adds FERRY users and identities to Rucio as account type USER.
Also applies analysis account attributes/policy to these accounts.
"""

import logging
import os

from rucio.client import Client
from rucio.common.exception import AccountNotFound, Duplicate

from FerryClient import FerryClient


# setup logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

# setup clients
ferry = FerryClient(logger=logger)
client = Client()

dry_run = True

ANALYSIS_ATTRIBUTES = [
    "add_rule",
    "add_replicas",
    "add_did",
    "add_dids",
    "update_replicas_states"
]


def main():
    unitname = os.getenv("FERRY_VO", "int")
    try:
        members = ferry.getAffiliationMembers(unitname)[0]
    except Exception as e:
        logger.error(f"Could not get users in affiliation {unitname}")
        logger.error(e)
        raise

    for user in members['users']:
        username = user['username']

        try:
            user = ferry.getUserInfo(username)
            if not user['status'] or user['banned']:
                continue
        except:
            continue

        try:
            userLdap = ferry.getUserLdapInfo(username)
            email = userLdap['mail']
        except Exception as e:
            logger.error(f"Cannot get userLdapInfo for {username}")
            logger.error(e)
            continue

        try:
           client.get_account(username)
        except AccountNotFound:
            logger.info(f"Account {username} not found. Adding...")
            if not dry_run:
                client.add_account(username, 'USER', email)

        if not dry_run:
            logger.info(f"Adding scope for user: {username}")
            try:
                client.add_scope(username, f'user.{username}')
            except Duplicate:
                logger.info(f"Scope for user {username} already exists")

        # add identities
        logger.info(f"Adding identities for {username}")
        dn = ferry.getUserCertificateDNs(unitname, username)
        if not dry_run:
            for d in dn:
                client.add_identity(username, d, "X509", email)

        # add attributes
        attributes = client.list_account_attributes(username)
        logger.info(f"Adding analysis attributes")
        for a in ANALYSIS_ATTRIBUTES:
            if not dry_run:
                try:
                    client.add_account_attribute(username, a, "1")
                except Duplicate as e:
                    logger.error(e)
                    continue

    # delete rucio accounts not in FERRY members
    rucio_accounts = client.list_accounts(account_type="USER")
    ferry_accounts = [m['username'] for m in members['users']]
    for a in rucio_accounts:
        if a['account'] not in ferry_accounts:
            logger.info(f"Disabling account {a}")
            if not dry_run:
                client.delete_account(a)


if __name__ == "__main__":
    main()