# Copyright 2016-2020 CERN for the benefit of the ATLAS collaboration.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors:
# - Vincent Garonne <vgaronne@gmail.com>, 2016
# - Cedric Serfon <cedric.serfon@cern.ch>, 2016-2018
# - Martin Barisits <martin.barisits@cern.ch>, 2017-2020
# - Mario Lassnig <mario.lassnig@cern.ch>, 2018-2020
# - Hannes Hansen <hannes.jakob.hansen@cern.ch>, 2018-2019
# - Andrew Lister <andrew.lister@stfc.ac.uk>, 2019
# - Ruturaj Gujar <ruturaj.gujar23@gmail.com>, 2019
# - Eric Vaandering, <ewv@fnal.gov>, 2020
# - Benedikt Ziemons <benedikt.ziemons@cern.ch>, 2020
# - Eli Chadwick <eli.chadwick@stfc.ac.uk>, 2020
# - Patrick Austin <patrick.austin@stfc.ac.uk>, 2020
# - Brandon White <bjwhite@fnal.gov>, 2020
#
# PY3K COMPATIBLE

import rucio.core.scope
from rucio.core.account import list_account_attributes, has_account_attribute
from rucio.core.identity import exist_identity_account
from rucio.core.lifetime_exception import list_exceptions
from rucio.core.rse import list_rse_attributes
from rucio.core.rse_expression_parser import parse_expression
from rucio.db.sqla.constants import IdentityType

import rucio.core.permission.generic

def has_permission(issuer, action, kwargs):
    """
    Checks if an account has the specified permission to
    execute an action with parameters.

    :param issuer: Account identifier which issues the command..
    :param action:  The action(API call) called by the account.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    perm = {
            'add_rule': perm_add_rule,
            'add_scope': perm_add_scope,
            'add_subscription': perm_add_subscription,
            'declare_bad_file_replicas': perm_declare_bad_file_replicas,
            'add_replicas': perm_add_replicas,
            'update_replicas_states': perm_update_replicas_states,
            'del_rule': perm_del_rule,
            'update_rule': perm_update_rule,
            'approve_rule': perm_approve_rule,
            'update_subscription': perm_update_subscription,
            'reduce_rule': perm_reduce_rule,
            'move_rule': perm_move_rule,
            'add_did': perm_add_did,
            'add_dids': perm_add_dids,
            'attach_dids': perm_attach_dids,
            'detach_dids': perm_detach_dids,
            'create_did_sample': perm_create_did_sample,
            'queue_requests': perm_queue_requests,
            'query_request': perm_query_request,
            'cancel_request': perm_cancel_request,
            'get_next': perm_get_next,
            'resurrect': perm_resurrect,
            'update_lifetime_exceptions': perm_update_lifetime_exceptions,
            'add_bad_pfns': perm_add_bad_pfns,
            'remove_did_from_followed': perm_remove_did_from_followed,
            'remove_dids_from_followed': perm_remove_dids_from_followed}

    if action not in perm:
        return rucio.core.permission.generic.has_permission(issuer, action, kwargs)

    return perm.get(action, perm_default)(issuer=issuer, kwargs=kwargs)


def _is_root(issuer):
    return issuer.external == 'root'


def perm_default(issuer, kwargs):
    """
    Default permission.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='admin')


def perm_add_rule(issuer, kwargs):
    """
    Checks if an account can add a replication rule.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    if kwargs['account'] == issuer and not kwargs['locked']:
        return True
    if (_is_root(issuer) or 
        has_account_attribute(account=issuer, key='admin') or
        has_account_attribute(account=issuer, key='add_rule')
    ):
        return True
    return False


def perm_add_scope(issuer, kwargs):
    """
    Checks if an account can add a scope to a account.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or issuer == kwargs.get('account') or has_account_attribute(account=issuer, key='add_scope')


def perm_add_subscription(issuer, kwargs):
    """
    Checks if an account can add a subscription.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    if (_is_root(issuer) or
        has_account_attribute(account=issuer, key='admin') or
        has_account_attribute(account=issuer, key='add_subscription')
    ):
        return True
    return False


def perm_add_did(issuer, kwargs):
    """
    Checks if an account can add an data identifier to a scope.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    # Check the accounts of the issued rules
    if not _is_root(issuer) and not has_account_attribute(account=issuer, key='admin'):
        for rule in kwargs.get('rules', []):
            if rule['account'] != issuer:
                return False

    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin')\
        or has_account_attribute(account=issuer, key='add_did')\
        or rucio.core.scope.is_scope_owner(scope=kwargs['scope'], account=issuer)\
        or kwargs['scope'].external == u'mock'


def perm_add_dids(issuer, kwargs):
    """
    Checks if an account can bulk add data identifiers.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    # Check the accounts of the issued rules
    if not _is_root(issuer) and not has_account_attribute(account=issuer, key='admin'):
        for did in kwargs['dids']:
            for rule in did.get('rules', []):
                if rule['account'] != issuer:
                    return False

    return _is_root(issuer) \
        or has_account_attribute(account=issuer, key='admin')\
        or has_account_attribute(account=issuer, key='add_dids')


def perm_attach_dids(issuer, kwargs):
    """
    Checks if an account can append an data identifier to the other data identifier.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin')\
        or has_account_attribute(account=issuer, key='attach_dids')\
        or rucio.core.scope.is_scope_owner(scope=kwargs['scope'], account=issuer)\
        or kwargs['scope'].external == 'mock'


def perm_create_did_sample(issuer, kwargs):
    """
    Checks if an account can create a sample of a data identifier collection.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin')\
        or has_account_attribute(account=issuer, key='create_did_sample')\
        or rucio.core.scope.is_scope_owner(scope=kwargs['scope'], account=issuer)\
        or kwargs['scope'].external == 'mock'


def perm_del_rule(issuer, kwargs):
    """
    Checks if an issuer can delete a replication rule.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed to call the API call, otherwise False
    """
    if (_is_root(issuer)
        or has_account_attribute(account=issuer, key='admin')
        or has_account_attribute(account=issuer, key='del_rule')
    ):
        return True
    return False


def perm_update_rule(issuer, kwargs):
    """
    Checks if an issuer can update a replication rule.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed to call the API call, otherwise False
    """
    if (_is_root(issuer)
        or has_account_attribute(account=issuer, key='admin')
        or has_account_attribute(account=issuer, key='update_rule')
    ):
        return True
    return False


def perm_approve_rule(issuer, kwargs):
    """
    Checks if an issuer can approve a replication rule.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed to call the API call, otherwise False
    """
    if (_is_root(issuer)
        or has_account_attribute(account=issuer, key='admin')
        or has_account_attribute(account=issuer, key='approve_rule')
    ):
        return True
    return False


def perm_reduce_rule(issuer, kwargs):
    """
    Checks if an issuer can reduce a replication rule.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed to call the API call, otherwise False
    """
    if (_is_root(issuer)
        or has_account_attribute(account=issuer, key='admin')
        or has_account_attribute(account=issuer, key='reduce_rule')
    ):
        return True
    return False


def perm_move_rule(issuer, kwargs):
    """
    Checks if an issuer can move a replication rule.

    :param issuer:   Account identifier which issues the command.
    :param kwargs:   List of arguments for the action.
    :returns:        True if account is allowed to call the API call, otherwise False
    """
    if (_is_root(issuer)
        or has_account_attribute(account=issuer, key='admin')
        or has_account_attribute(account=issuer, key='move_rule')
    ):
        return True
    return False


def perm_update_subscription(issuer, kwargs):
    """
    Checks if an account can update a subscription.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    if (_is_root(issuer)
        or has_account_attribute(account=issuer, key='admin')
        or has_account_attribute(account=issuer, key='update_subscription')
    ):
        return True

    return False


def perm_detach_dids(issuer, kwargs):
    """
    Checks if an account can detach an data identifier from the other data identifier.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    return perm_attach_dids(issuer, kwargs)


def perm_declare_bad_file_replicas(issuer, kwargs):
    """
    Checks if an account can declare bad file replicas.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='declare_bad_file_replicas')


def perm_add_replicas(issuer, kwargs):
    """
    Checks if an account can add replicas.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    return str(kwargs.get('rse', '')).endswith('SCRATCHDISK')\
        or str(kwargs.get('rse', '')).endswith('USERDISK')\
        or str(kwargs.get('rse', '')).endswith('MOCK')\
        or str(kwargs.get('rse', '')).endswith('LOCALGROUPDISK')\
        or _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin')\
        or has_account_attribute(account=issuer, key='add_replicas')


def perm_update_replicas_states(issuer, kwargs):
    """
    Checks if an account can delete replicas.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin')\
        or has_account_attribute(account=issuer, key='update_replicas_states')


def perm_queue_requests(issuer, kwargs):
    """
    Checks if an account can submit transfer or deletion requests on destination RSEs for data identifiers.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='queue_requests')


def perm_query_request(issuer, kwargs):
    """
    Checks if an account can query a request.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='query_requests')


def perm_cancel_request(issuer, kwargs):
    """
    Checks if an account can cancel a request.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='cancel_request')


def perm_get_next(issuer, kwargs):
    """
    Checks if an account can retrieve the next request matching the request type and state.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='get_next')


def perm_resurrect(issuer, kwargs):
    """
    Checks if an account can resurrect DIDS.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed to call the API call, otherwise False
    """
    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin')\
        or has_account_attribute(account=issuer, key='resurrect')


def perm_update_lifetime_exceptions(issuer, kwargs):
    """
    Checks if an account can approve/reject Lifetime Model exceptions.

    :param issuer: Account identifier which issues the command.
    :returns: True if account is allowed to call the API call, otherwise False
    """
    if kwargs['vo'] is not None:
        exceptions = next(list_exceptions(exception_id=kwargs['exception_id'], states=False))
        if exceptions['scope'].vo != kwargs['vo']:
            return False
    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin')\
        or has_account_attribute(account=issuer, key='update_lifetime_exceptions')


def perm_add_bad_pfns(issuer, kwargs):
    """
    Checks if an account can declare bad PFNs.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='add_bad_pfns')


def perm_remove_did_from_followed(issuer, kwargs):
    """
    Checks if an account can remove did from followed table.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin')\
        or has_account_attribute(account=issuer, key='remove_did_from_followed')\
        or kwargs['account'] == issuer\
        or kwargs['scope'].external == 'mock'


def perm_remove_dids_from_followed(issuer, kwargs):
    """
    Checks if an account can bulk remove dids from followed table.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :returns: True if account is allowed, otherwise False
    """
    if (_is_root(issuer) 
        or has_account_attribute(account=issuer, key='admin')
        or has_account_attribute(account=issuer, key='remove_dids_from_followed')
    ):
        return True
    if not kwargs['account'] == issuer:
        return False
    return True
