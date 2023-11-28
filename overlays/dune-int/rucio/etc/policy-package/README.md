# DUNERucioPolicy
This is the prototype Rucio policy package for DUNE.

## How to use this policy package
* The MetaCat Python package is required for the lfn2pfn algorithm. It can be installed with `pip install metacat`.
* Make sure the directory containing the `DUNERucioPolicy` directory is in the `PYTHONPATH` for the Rucio server.
* Set `package = DUNERucioPolicy` in the `policy` section of the Rucio configuration file.
* Set `sam_base_url = <base URL>` in the `policy` section of the Rucio configuration file. The default value for this URL is `https://samweb.fnal.gov:8483/sam/dune-test/api`.
* Set `metacat_base_url = <base URL>` in the `policy` section of the Rucio configuration file. The default value for this URL is `https://dbdata0vm.fnal.gov:9443/dune_meta_demo/app`.

## Source files
* `__init__.py` - registers the SURL and LFN2PFN algorithms when the package is loaded.
* `lfn2pfn.py` - contains the DUNE lfn2pfn algorithm which queries the Metacat metadata service and constructs PFNs based on the metadata returned.
* `path_gen.py` - contains the DUNE SURL algorithm which currently queries the SAM metadata service to get required information on the file.
* `permission.py` - permission functions for the policy package.
* `schema.py` - schema functions and data for the policy package. Currently just a copy of the generic code with no DUNE-specific customisation.

## Issues
* Unlike other SURL algorithms, the DUNE algorithm may throw an exception (if, for example, it is unable to contact the SAM service). The calling code within Rucio may require changes to handle this more gracefully.
* The same applies to the LFN2PFN algorithm, which can also throw exceptions.
* Future versions of the SURL algorithm may require additional arguments. Rucio could be modified to pass in a dictionary of additional file information to SURL algorithms that need it.
