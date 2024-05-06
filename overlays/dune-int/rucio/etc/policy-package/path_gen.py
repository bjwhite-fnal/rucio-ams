import requests
import urllib
from rucio.common import config
from rucio.common.exception import ServiceUnavailable
from datetime import datetime
import os

sam_base = None


def construct_surl_dune_sam(dsn, scope, name):
    global sam_base

    if sam_base is None:
        sam_base = config.config_get('policy', 'sam_base_url')
        if sam_base is None:
            sam_base = 'https://samweb.fnal.gov:8483/sam/dune-test/api'

    url = '%s/files/name/%s/destination?format=json' % (sam_base, urllib.quote(name, ''))

    try:
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()
    except Exception as ex:
        raise ServiceUnavailable("Error querying SAM")

    destination = result["destination"]
    if not destination.startswith('/'):
        destination = '/' + destination
    if destination.endswith('/'):
        destination += name
    else:
        destination += '/' + name
    return destination


def construct_surl_dune_metacat(dsn, scope, name):
    from metacat.webapi import MetaCatClient

    # current URL: https://metacat.fnal.gov:9443/dune_meta_demo/app
    metacat_url = config.config_get('policy', 'metacat_base_url', raise_exception=False) or os.environ.get("METACAT_SERVER_URL")
    if metacat_url is None:
        raise ValueError("MetaCat client URL is not configured")

    metacat_client = MetaCatClient(metacat_url)

    def get_metadata_field(metadata, field):
        if field in metadata:
            return metadata[field]
        if field.lower() in metadata:
            return metadata[field.lower()]
        return 'None'

    jsondata = metacat_client.get_file(name=name, namespace=scope)
    metadata = jsondata["metadata"]

    # determine year from timestamps
    timestamp = None
    if 'core.start_time' in metadata:
        timestamp = metadata['core.start_time']
    elif 'core.end_time' in metadata:
        timestamp = metadata['core.end_time']
    elif 'created_timestamp' in jsondata:
        timestamp = jsondata['created_timestamp']
    if timestamp is None:
        year = 'None'
    else:
        dt = datetime.utcfromtimestamp(timestamp)
        year = str(dt.year)

    # determine hashes from run number
    run_number = 0
    if 'core.runs' in metadata:
        run_number = int(metadata['core.runs'][0])
        
    hash1 = "%02d" % ((run_number // 1000000) % 100)
    hash2 = "%02d" % ((run_number // 10000) % 100)
    hash3 = "%02d" % ((run_number // 100) % 100)
    hash4 = "%02d" % (run_number % 100)

    run_type = get_metadata_field(metadata, 'core.run_type')
    data_tier = get_metadata_field(metadata, 'core.data_tier')
    file_type = get_metadata_field(metadata, 'core.file_type')
    data_stream = get_metadata_field(metadata, 'core.data_stream')
    data_campaign = get_metadata_field(metadata, 'DUNE.campaign')
    filename = name
    
    pfn = run_type + '/' + data_tier + '/' + year + '/' + file_type + '/' + data_stream + '/' + data_campaign + '/' + hash1 + '/' + hash2 + '/' + hash3 + '/' + hash4 + '/' + filename

    return pfn
