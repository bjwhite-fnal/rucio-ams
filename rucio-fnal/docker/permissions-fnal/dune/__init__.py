from .path_gen import construct_surl_dune
from .lfn2pfn import lfn2pfn_DUNE

SUPPORTED_VERSION="1.20.7"

def get_lfn2pfn_algorithms():
    return { 'DUNE': lfn2pfn_DUNE }

def get_surl_algorithms():
    return { 'DUNE': construct_surl_dune }
