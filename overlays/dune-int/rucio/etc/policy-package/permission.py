# Copyright 2016-2022 CERN for the benefit of the ATLAS collaboration.
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
# - James Perr <j.perry@epcc.ed.ac.uk>, 2022
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

import os
from metacat.webapi import MetaCatClient

metacat_client = MetaCatClient()				# will read env. METACAT_SERVER_URL by default


def has_permission(issuer, action, kwargs, session=None):
    """
    Checks if an account has the specified permission to
    execute an action with parameters.

    :param issuer: Account identifier which issues the command..
    :param action:  The action(API call) called by the account.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    perm = {
            'add_rule': perm_add_rule,
            'add_scope': perm_add_scope,
            'add_rse': perm_add_rse,
            'add_protocol': perm_add_protocol,
            'del_protocol': perm_del_protocol,
            'update_protocol': perm_update_protocol,
            'add_subscription': perm_add_subscription,
            'declare_bad_file_replicas': perm_declare_bad_file_replicas,
            'add_replicas': perm_add_replicas,
            'update_replicas_states': perm_update_replicas_states,
            'add_rse_attribute': perm_add_rse_attribute,
            'del_rse_attribute': perm_del_rse_attribute,
            'del_rse': perm_del_rse,
            'set_rse_usage': perm_set_rse_usage,
            'set_rse_limits': perm_set_rse_limits,
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
            'remove_dids_from_followed': perm_remove_dids_from_followed,
            'set_local_account_limit': perm_set_local_account_limit,
            'set_global_account_limit': perm_set_global_account_limit,
            'delete_local_account_limit': perm_delete_local_account_limit,
            'delete_global_account_limit': perm_delete_global_account_limit,
            'get_local_account_usage': perm_get_local_account_usage,
            'get_global_account_usage': perm_get_global_account_usage,
            'add_distance': perm_add_distance,
            'update_distance': perm_update_distance,
            'access_rule_vo': perm_access_rule_vo}

    if action not in perm:
        return rucio.core.permission.generic.has_permission(issuer, action, kwargs, session=session)

    return perm.get(action, perm_default)(issuer=issuer, kwargs=kwargs, session=session)


def _is_root(issuer):
    return issuer.external == 'root'


def perm_default(issuer, kwargs, session=None):
    """
    Default permission.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session)


def perm_add_rule(issuer, kwargs, session=None):
    """
    Checks if an account can add a replication rule.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    if kwargs['account'] == issuer and not kwargs['locked']:
        return True
    if (_is_root(issuer) or 
        has_account_attribute(account=issuer, key='admin', session=session) or
        has_account_attribute(account=issuer, key='add_rule', session=session)
    ):
        return True
    return False


def perm_add_scope(issuer, kwargs, session=None):
    """
    Checks if an account can add a scope to a account.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or issuer == kwargs.get('account') or has_account_attribute(account=issuer, key='add_scope', session=session)


def perm_add_rse(issuer, kwargs, session=None):
    """
    Checks if an account can add a RSE.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) or has_account_attribute(account=issuer, key='add_rse', session=session)


def perm_add_subscription(issuer, kwargs, session=None):
    """
    Checks if an account can add a subscription.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    if (_is_root(issuer) or
        has_account_attribute(account=issuer, key='admin', session=session) or
        has_account_attribute(account=issuer, key='add_subscription', session=session)
    ):
        return True
    return False


def _files_exist(lst):
    dids = set(item["scope"].external+":"+item["name"] for item in lst)    
    files = metacat_client.get_files([{"did":did} for did in dids])
    return len(files) == len(dids)


def _dataset_exists(dataset):
    return metacat_client.get_dataset(did=dataset["scope"].external+":"+dataset["name"]) is not None


def perm_add_did(issuer, kwargs, session=None):
    """
    Checks if an account can add an data identifier to a scope.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """

    if kwargs["type"] == "FILE" and not _files_exist([kwargs]):
        return False

    if (kwargs["type"] == "DATASET" or kwargs["type"] == "CONTAINER") and not _dataset_exists(kwargs):
        return False

    # Check the accounts of the issued rules
    if not _is_root(issuer) and not has_account_attribute(account=issuer, key='admin', session=session):
        for rule in kwargs.get('rules', []):
            if rule['account'] != issuer:
                return False

    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin', session=session)\
        or has_account_attribute(account=issuer, key='add_did', session=session)\
        or rucio.core.scope.is_scope_owner(scope=kwargs['scope'], account=issuer, session=session)\
        or kwargs['scope'].external == u'mock'


def perm_add_dids(issuer, kwargs, session=None):
    """
    Checks if an account can bulk add data identifiers.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    
    files = [did for did in kwargs if did.get("type") in ("F", "FILE")]

    if files and not _files_exist(files):
        return False
    
    # Check the accounts of the issued rules
    if not _is_root(issuer) and not has_account_attribute(account=issuer, key='admin', session=session):
        for did in kwargs['dids']:
            for rule in did.get('rules', []):
                if rule['account'] != issuer:
                    return False

    return _is_root(issuer) \
        or has_account_attribute(account=issuer, key='admin', session=session)\
        or has_account_attribute(account=issuer, key='add_dids', session=session)


def perm_attach_dids(issuer, kwargs, session=None):
    """
    Checks if an account can append an data identifier to the other data identifier.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin', session=session)\
        or has_account_attribute(account=issuer, key='attach_dids', session=session)\
        or rucio.core.scope.is_scope_owner(scope=kwargs['scope'], account=issuer, session=session)\
        or kwargs['scope'].external == 'mock'


def perm_create_did_sample(issuer, kwargs, session=None):
    """
    Checks if an account can create a sample of a data identifier collection.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin', session=session)\
        or has_account_attribute(account=issuer, key='create_did_sample', session=session)\
        or rucio.core.scope.is_scope_owner(scope=kwargs['scope'], account=issuer, session=session)\
        or kwargs['scope'].external == 'mock'


def perm_del_rule(issuer, kwargs, session=None):
    """
    Checks if an issuer can delete a replication rule.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed to call the API call, otherwise False
    """
    if (_is_root(issuer)
        or has_account_attribute(account=issuer, key='admin', session=session)
        or has_account_attribute(account=issuer, key='del_rule', session=session)
    ):
        return True
    return False


def perm_update_rule(issuer, kwargs, session=None):
    """
    Checks if an issuer can update a replication rule.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed to call the API call, otherwise False
    """
    if (_is_root(issuer)
        or has_account_attribute(account=issuer, key='admin', session=session)
        or has_account_attribute(account=issuer, key='update_rule', session=session)
    ):
        return True
    return False


def perm_approve_rule(issuer, kwargs, session=None):
    """
    Checks if an issuer can approve a replication rule.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed to call the API call, otherwise False
    """
    if (_is_root(issuer)
        or has_account_attribute(account=issuer, key='admin', session=session)
        or has_account_attribute(account=issuer, key='approve_rule', session=session)
    ):
        return True
    return False


def perm_reduce_rule(issuer, kwargs, session=None):
    """
    Checks if an issuer can reduce a replication rule.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed to call the API call, otherwise False
    """
    if (_is_root(issuer)
        or has_account_attribute(account=issuer, key='admin', session=session)
        or has_account_attribute(account=issuer, key='reduce_rule', session=session)
    ):
        return True
    return False


def perm_move_rule(issuer, kwargs, session=None):
    """
    Checks if an issuer can move a replication rule.

    :param issuer:   Account identifier which issues the command.
    :param kwargs:   List of arguments for the action.
    :param session: The DB session to use
    :returns:        True if account is allowed to call the API call, otherwise False
    """
    if (_is_root(issuer)
        or has_account_attribute(account=issuer, key='admin', session=session)
        or has_account_attribute(account=issuer, key='move_rule', session=session)
    ):
        return True
    return False


def perm_update_subscription(issuer, kwargs, session=None):
    """
    Checks if an account can update a subscription.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    if (_is_root(issuer)
        or has_account_attribute(account=issuer, key='admin', session=session)
        or has_account_attribute(account=issuer, key='update_subscription', session=session)
    ):
        return True

    return False


def perm_detach_dids(issuer, kwargs, session=None):
    """
    Checks if an account can detach an data identifier from the other data identifier.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return perm_attach_dids(issuer, kwargs, session)


def perm_declare_bad_file_replicas(issuer, kwargs, session=None):
    """
    Checks if an account can declare bad file replicas.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='declare_bad_file_replicas', session=session)


def perm_add_replicas(issuer, kwargs, session=None):
    """
    Checks if an account can add replicas.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return str(kwargs.get('rse', '')).endswith('SCRATCHDISK')\
        or str(kwargs.get('rse', '')).endswith('USERDISK')\
        or str(kwargs.get('rse', '')).endswith('MOCK')\
        or str(kwargs.get('rse', '')).endswith('LOCALGROUPDISK')\
        or _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin', session=session)\
        or has_account_attribute(account=issuer, key='add_replicas', session=session)


def perm_update_replicas_states(issuer, kwargs, session=None):
    """
    Checks if an account can delete replicas.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin', session=session)\
        or has_account_attribute(account=issuer, key='update_replicas_states', session=session)


def perm_add_rse_attribute(issuer, kwargs, session=None):
    """
    Checks if an account can add a RSE attribute.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    if _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) or has_account_attribute(account=issuer, key='add_rse_attribute', session=session):
        return True
    return False


def perm_queue_requests(issuer, kwargs, session=None):
    """
    Checks if an account can submit transfer or deletion requests on destination RSEs for data identifiers.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='queue_requests', session=session)


def perm_query_request(issuer, kwargs, session=None):
    """
    Checks if an account can query a request.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='query_requests', session=session)


def perm_cancel_request(issuer, kwargs, session=None):
    """
    Checks if an account can cancel a request.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='cancel_request', session=session)


def perm_get_next(issuer, kwargs, session=None):
    """
    Checks if an account can retrieve the next request matching the request type and state.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='get_next', session=session)


def perm_resurrect(issuer, kwargs, session=None):
    """
    Checks if an account can resurrect DIDS.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed to call the API call, otherwise False
    """
    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin', session=session)\
        or has_account_attribute(account=issuer, key='resurrect', session=session)


def perm_update_lifetime_exceptions(issuer, kwargs, session=None):
    """
    Checks if an account can approve/reject Lifetime Model exceptions.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed to call the API call, otherwise False
    """
    if kwargs['vo'] is not None:
        exceptions = next(list_exceptions(exception_id=kwargs['exception_id'], states=False, session=session))
        if exceptions['scope'].vo != kwargs['vo']:
            return False
    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin', session=session)\
        or has_account_attribute(account=issuer, key='update_lifetime_exceptions', session=session)


def perm_add_bad_pfns(issuer, kwargs, session=None):
    """
    Checks if an account can declare bad PFNs.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='add_bad_pfns', session=session)


def perm_remove_did_from_followed(issuer, kwargs, session=None):
    """
    Checks if an account can remove did from followed table.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer)\
        or has_account_attribute(account=issuer, key='admin', session=session)\
        or has_account_attribute(account=issuer, key='remove_did_from_followed', session=session)\
        or kwargs['account'] == issuer\
        or kwargs['scope'].external == 'mock'


def perm_remove_dids_from_followed(issuer, kwargs, session=None):
    """
    Checks if an account can bulk remove dids from followed table.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    if (_is_root(issuer) 
        or has_account_attribute(account=issuer, key='admin', session=session)
        or has_account_attribute(account=issuer, key='remove_dids_from_followed', session=session)
    ):
        return True
    if not kwargs['account'] == issuer:
        return False
    return True

def perm_add_protocol(issuer, kwargs, session=None):
    """
    Checks if an account can add a protocol to an RSE.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) or has_account_attribute(account=issuer, key='add_protocol', session=session)


def perm_del_protocol(issuer, kwargs, session=None):
    """
    Checks if an account can delete protocols from an RSE.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) or has_account_attribute(account=issuer, key='add_protocol', session=session)


def perm_update_protocol(issuer, kwargs, session=None):
    """
    Checks if an account can update protocols of an RSE.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) or has_account_attribute(account=issuer, key='add_protocol', session=session)

def perm_del_rse_attribute(issuer, kwargs, session=None):
    """
    Checks if an account can delete a RSE attribute.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    if _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) or has_account_attribute(account=issuer, key='del_rse_attribute', session=session):
        return True
    return False


def perm_del_rse(issuer, kwargs, session=None):
    """
    Checks if an account can delete a RSE.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) or has_account_attribute(account=issuer, key='del_rse', session=session)


def perm_set_rse_usage(issuer, kwargs, session=None):
    """
    Checks if an account can set RSE usage information.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed to call the API call, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='set_rse_usage', session=session)


def perm_set_rse_limits(issuer, kwargs, session=None):
    """
    Checks if an account can set RSE limits.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed to call the API call, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) or has_account_attribute(account=issuer, key='set_rse_limits', session=session)


def perm_set_local_account_limit(issuer, kwargs, session=None):
    """
    Checks if an account can set an account limit.

    :param account: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    if _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) or has_account_attribute(account=issuer, key='set_local_account_limit', session=session):
        return True
    # Check if user is a country admin
    admin_in_country = []
    for kv in list_account_attributes(account=issuer, session=session):
        if kv['key'].startswith('country-') and kv['value'] == 'admin':
            admin_in_country.append(kv['key'].partition('-')[2])
    if admin_in_country and list_rse_attributes(rse_id=kwargs['rse_id'], session=session).get('country') in admin_in_country:
        return True
    return False


def perm_set_global_account_limit(issuer, kwargs, session=None):
    """
    Checks if an account can set a global account limit.

    :param account: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    if _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) or has_account_attribute(account=issuer, key='set_global_account_limit', session=session):
        return True
    # Check if user is a country admin
    admin_in_country = set()
    for kv in list_account_attributes(account=issuer, session=session):
        if kv['key'].startswith('country-') and kv['value'] == 'admin':
            admin_in_country.add(kv['key'].partition('-')[2])
    resolved_rse_countries = {list_rse_attributes(rse_id=rse['rse_id'], session=session).get('country') for rse in parse_expression(kwargs['rse_expression'])}
    if resolved_rse_countries.issubset(admin_in_country):
        return True
    return False


def perm_delete_local_account_limit(issuer, kwargs, session=None):
    """
    Checks if an account can delete an account limit.

    :param account: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    if _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) or has_account_attribute(account=issuer, key='delete_local_account_limit', session=session):
        return True
    # Check if user is a country admin
    admin_in_country = []
    for kv in list_account_attributes(account=issuer, session=session):
        if kv['key'].startswith('country-') and kv['value'] == 'admin':
            admin_in_country.append(kv['key'].partition('-')[2])
    if admin_in_country and list_rse_attributes(rse_id=kwargs['rse_id'], session=session).get('country') in admin_in_country:
        return True
    return False


def perm_delete_global_account_limit(issuer, kwargs, session=None):
    """
    Checks if an account can delete a global account limit.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    if _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) or has_account_attribute(account=issuer, key='delete_global_account_limit', session=session):
        return True
    # Check if user is a country admin
    admin_in_country = set()
    for kv in list_account_attributes(account=issuer, session=session):
        if kv['key'].startswith('country-') and kv['value'] == 'admin':
            admin_in_country.add(kv['key'].partition('-')[2])
    if admin_in_country:
        resolved_rse_countries = {list_rse_attributes(rse_id=rse['rse_id'], session=session).get('country') for rse in parse_expression(kwargs['rse_expression'])}
        if resolved_rse_countries.issubset(admin_in_country):
            return True
    return False


def perm_get_local_account_usage(issuer, kwargs, session=None):
    """
    Checks if an account can get the account usage of an account.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    if _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) \
        or kwargs.get('account') == issuer or has_account_attribute(account=issuer, key='get_local_account_usage', session=session):
        return True
    # Check if user is a country admin
    for kv in list_account_attributes(account=issuer, session=session):
        if kv['key'].startswith('country-') and kv['value'] == 'admin':
            return True
    return False


def perm_get_global_account_usage(issuer, kwargs, session=None):
    """
    Checks if an account can get the account usage of an account.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed, otherwise False
    """
    if _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) \
        or kwargs.get('account') == issuer or has_account_attribute(account=issuer, key='get_global_account_usage', session=session):
        return True

    # Check if user is a country admin for all involved countries
    admin_in_country = set()
    for kv in list_account_attributes(account=issuer, session=session):
        if kv['key'].startswith('country-') and kv['value'] == 'admin':
            admin_in_country.add(kv['key'].partition('-')[2])
    resolved_rse_countries = {list_rse_attributes(rse_id=rse['rse_id'], session=session).get('country')
                              for rse in parse_expression(kwargs['rse_exp'])}

    if resolved_rse_countries.issubset(admin_in_country):
        return True
    return False


def perm_add_distance(issuer, kwargs, session=None):
    """
    Checks if an account can add a distance between RSEs.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed to call the API call, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) or has_account_attribute(account=issuer, key='add_distance', session=session)


def perm_update_distance(issuer, kwargs, session=None):
    """
    Checks if an account can add a distance between RSEs.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed to call the API call, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) or has_account_attribute(account=issuer, key='update_distance', session=session)


def perm_access_rule_vo(issuer, kwargs, session=None):
    """
    Checks if an account can add a distance between RSEs.

    :param issuer: Account identifier which issues the command.
    :param kwargs: List of arguments for the action.
    :param session: The DB session to use
    :returns: True if account is allowed to call the API call, otherwise False
    """
    return _is_root(issuer) or has_account_attribute(account=issuer, key='admin', session=session) or has_account_attribute(account=issuer, key='access_rule_vo', session=session)
