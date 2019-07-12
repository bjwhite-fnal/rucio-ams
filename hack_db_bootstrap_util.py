# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2013-2016
# - Mario Lassnig, <mario.lassnig@cern.ch>, 2013-2014, 2017-2018
# - Martin Barisits, <martin.barisits@cern.ch>, 2014
# - Hannes Hansen, <hannes.jakob.hansen@cern.ch>, 2019
#
# PY3K COMPATIBLE

from __future__ import print_function
from datetime import datetime
from traceback import format_exc

from alembic import command
from alembic.config import Config

from sqlalchemy import func
from sqlalchemy.engine import reflection
from sqlalchemy.schema import MetaData, Table, DropTable, ForeignKeyConstraint, DropConstraint
from sqlalchemy.sql.expression import select, text

from rucio.common.config import config_get
from rucio.core.account_counter import create_counters_for_new_account
from rucio.db.sqla import session, models
from rucio.db.sqla.constants import AccountStatus, AccountType, IdentityType


def build_database(echo=True, tests=False):
    """ Applies the schema to the database. Run this command once to build the database. """
    engine = session.get_engine(echo=echo)
    models.register_models(engine)

    # Put the database under version control
    alembic_cfg = Config(config_get('alembic', 'cfg'))
    command.stamp(alembic_cfg, "head")


def dump_schema():
    """ Creates a schema dump to a specific database. """
    engine = session.get_dump_engine()
    models.register_models(engine)


def destroy_database(echo=True):
    """ Removes the schema from the database. Only useful for test cases or malicious intents. """
    engine = session.get_engine(echo=echo)
    models.unregister_models(engine)


def drop_everything(echo=True):
    """ Pre-gather all named constraints and table names, and drop everything. This is better than using metadata.reflect();
        metadata.drop_all() as it handles cyclical constraints between tables.
        Ref. http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything
    """
    engine = session.get_engine(echo=echo)
    conn = engine.connect()

    # the transaction only applies if the DB supports
    # transactional DDL, i.e. Postgresql, MS SQL Server
    trans = conn.begin()

    inspector = reflection.Inspector.from_engine(engine)

    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in
    # a transaction.
    metadata = MetaData()

    tbs = []
    all_fks = []

    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(ForeignKeyConstraint((), (), name=fk['name']))
        t = Table(table_name, metadata, *fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        try:
            print(str(DropConstraint(fkc)) + ';')
            conn.execute(DropConstraint(fkc))
        except:
            print(format_exc())

    for table in tbs:
        try:
            print(str(DropTable(table)).strip() + ';')
            conn.execute(DropTable(table))
        except:
            print(format_exc())

    trans.commit()


def create_root_account():
    """ Inserts the default root account to an existing database. Make sure to change the default password later. """
    x509_id = '/DC=org/DC=cilogon/C=US/O=Fermi National Accelerator Laboratory/OU=People/CN=Brandon White/CN=UID:bjwhite'
    x509_email = 'bjwhite@fnal.gov'

    try:
        x509_id = config_get('bootstrap', 'x509_identity')
        x509_email = config_get('bootstrap', 'x509_email')
    except:
        pass
        # print 'Config values are missing (check rucio.cfg{.template}). Using hardcoded defaults.'

    s = session.get_session()

    account = models.Account(account='root', account_type=AccountType.SERVICE, status=AccountStatus.ACTIVE)

    # X509 authentication
    # Brandon White: bjwhite@fnal.gov
    identity = models.Identity(identity=x509_id, identity_type=IdentityType.X509, email=x509_email)
    iaa = models.IdentityAccountAssociation(identity=identity.identity, identity_type=identity.identity_type, account=account.account, is_default=True)

    # Account counters
    create_counters_for_new_account(account='root', session=s)

    # Apply
    s.add_all([account, identity])
    s.commit()
    s.add_all([iaa])
    s.commit()


def get_db_time():
    """ Gives the utc time on the db. """
    s = session.get_session()
    try:
        storage_date_format = None
        if s.bind.dialect.name == 'oracle':
            query = select([text("sys_extract_utc(systimestamp)")])
        elif s.bind.dialect.name == 'mysql':
            query = select([text("utc_timestamp()")])
        elif s.bind.dialect.name == 'sqlite':
            query = select([text("datetime('now', 'utc')")])
            storage_date_format = '%Y-%m-%d  %H:%M:%S'
        else:
            query = select([func.current_date()])

        for now, in s.execute(query):
            if storage_date_format:
                return datetime.strptime(now, storage_date_format)
            return now

    finally:
        s.remove()
