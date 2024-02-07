from sqlalchemy.exc import IntegrityError

from rucio.common.config import config_get
from rucio.common.types import InternalAccount
from rucio.core.account_counter import create_counters_for_new_account
from rucio.db.sqla import models
from rucio.db.sqla.constants import AccountStatus, AccountType, IdentityType
from rucio.db.sqla.session import get_session
from rucio.db.sqla.util import (build_database, create_base_vo)


def create_root_account(create_counters=True):
    """
    Inserts the default root account to an existing database. Make sure to change the default password later.

    :param create_counters: If True, create counters for the new account at existing RSEs.
    """

    multi_vo = bool(config_get('common', 'multi_vo', False, False))

    x509_id = '/C=CH/ST=Geneva/O=CERN/OU=PH-ADP-CO/CN=DDMLAB Client Certificate/emailAddress=ph-adp-ddm-lab@cern.ch'
    x509_email = 'ph-adp-ddm-lab@cern.ch'

    try:
        x509_id = config_get('bootstrap', 'x509_identity')
        x509_email = config_get('bootstrap', 'x509_email')
    except:
        pass
        # print 'Config values are missing (check rucio.cfg{.template}). Using hardcoded defaults.'

    s = get_session()

    if multi_vo:
        access = 'super_root'
    else:
        access = 'root'

    account = models.Account(account=InternalAccount(access, 'def'), account_type=AccountType.SERVICE, status=AccountStatus.ACTIVE)

    # X509 authentication
    identity2 = models.Identity(identity=x509_id, identity_type=IdentityType.X509, email=x509_email)
    iaa2 = models.IdentityAccountAssociation(identity=identity2.identity, identity_type=identity2.identity_type, account=account.account, is_default=True)

    # Account counters
    if create_counters:
        create_counters_for_new_account(account=account.account, session=s)

    # Apply
    try:
        s.add(identity2)
        s.commit()
    except IntegrityError:
        # Identities may already be in the DB when running multi-VO conversion
        s.rollback()
    s.add(account)
    s.commit()
    s.add_all([iaa2])
    s.commit()


if __name__ == '__main__':
    build_database()
    create_base_vo()
    create_root_account()
