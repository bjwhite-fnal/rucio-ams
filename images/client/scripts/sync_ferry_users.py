#!/usr/bin/env python3
"""
Script to sync FERRY users to Rucio based on vo/afffiliation

Adds FERRY users and identities to Rucio as account type USER.
Also applies analysis account attributes/policy to these accounts.
"""

import argparse
from dataclasses import dataclass, asdict
import logging
import os
import sys

from rucio.client import Client
from rucio.common.exception import AccountNotFound, Duplicate

from FerryClient import FerryClient

# setup logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.INFO)
logger.addHandler(ch)

# setup clients
ferry = FerryClient(logger=logger)
client = Client()

# analysis account attributes
ANALYSIS_ATTRIBUTES = [
    "add_rule",
    "add_replicas",
    "add_did",
    "add_dids",
    "update_replicas_states"
]


@dataclass
class User:
    """
    Dataclass that has values required to create
    a Rucio Account
    """
    name: str
    email: str
    identities: list[str]
    create: bool = False


def sync_ferry_users(commit=False, delete_accounts=False, vo='int'):
    """
    Fetches users from FERRY and adds them to Rucio with analysis attributes
    """
    unitname = os.getenv("FERRY_VO", vo)
    filtered_users = os.getenv("FILTER_USERS", None)

    try:
        members = ferry.getAffiliationMembers(unitname)[0]
    except Exception as e:
        logger.error(f"Could not get users in affiliation {unitname}")
        logger.error(e)
        raise

    # filter out specific users
    if filtered_users:
        filtered = filtered_users.split(',')
        members['users'] = [m for m in members['users'] if m['username'] in filtered]

    users_to_add = [] 
    for user in members['users']:
        username = user['username']

        # ignore banned or deactivated users
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
            logger.error(f"Could not get userLdapInfo for {username}")
            logger.error(e)
            continue

        create = False
        try:
           client.get_account(username)
        except AccountNotFound:
            logger.info(f"Account {username} not found. Will create an account.")
            create = True

        # fetch identities
        logger.info(f"Fetching identities for {username}")
        dn = ferry.getUserCertificateDNs(unitname, username)

        users_to_add.append(User(name=username, email=email, identities=dn, create=create))
    
    # Add or update users to Rucio
    if commit:
        for user in users_to_add:
            add_user(user)

    # delete rucio accounts not in FERRY members or if their status has changed
    if delete_accounts:
        delete_users(members, commit)


def add_user(user: User):
    """
    Add users to Rucio
    """
    username = user.name

    # create user, if they do not exist
    if user.create:
        logger.info(f"Creating account for {username}")
        client.add_account(username, 'USER', user.email)

    # create a scope
    logger.info(f"Adding scope for user: {username}")
    try:
        client.add_scope(username, f'user.{username}')
    except Duplicate:
        logger.info(f"Scope for user {username} already exists")

    # add user identities
    logger.info(f"Adding identities for {username}")
    for d in user.identities:
        try:
            client.add_identity(username, d, "X509", user.email)
        except Duplicate as e:
            logger.info(e)
            continue

    # add attributes
    logger.info(f"Adding analysis attributes")
    for a in ANALYSIS_ATTRIBUTES:
        try:
            client.add_account_attribute(username, a, "1")
        except Duplicate as e:
            logger.error(e)
            continue


def delete_users(members, commit=False):
    """
    Checks and delete/disable users from Rucio
    """
    rucio_accounts = client.list_accounts(account_type="USER")
    ferry_accounts = [m['username'] for m in members['users']]
    for a in rucio_accounts:
        if a['account'] not in ferry_accounts:
            logger.info(f"Disabling account {a}, account not affiliated")
            if commit:
                client.delete_account(a)
        else:
            index = ferry_accounts.index(a['account'])
            user = members[index]
            if not user['status'] or user['banned']:
                logger.info(f"Disabling account {a}, FERRY disabled or banned")
                if commit:
                    client.delete_account(a)


def main():
    parser = argparse.ArgumentParser(
        description='Sync FERRY Users',
        epilog='Syncs FERRY Users of a VO with Rucio')
    parser.add_argument('--commit',
                        action='store_true')
    parser.add_argument('--delete_accounts',
                        action='store_true')

    args = parser.parse_args()

    sync_ferry_users(commit=args.commit, delete_accounts=args.delete_accounts)


if __name__ == "__main__":
    main()