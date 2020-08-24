# get_full_configs

## Description
Nothing fancy, reads from a list of hosts and fetches their full config.  Creates subdirectories for each host inside of config_output.  If run consecutively and changes are detected based on filehash it will write the diff to a file in that subfolder as well as rename the old current config to OLD_CONFIG_RENAMED_(DATE).  The list of diffs in a file will also share this same date to help correlate the changes.

### Options

**--username** - pass this argument with the username to use to connect to hosts, the default is 'admin'

**--file_name** - the name of the file to read hosts from, the default is 'host_list.xlsx' and the format is in that file

**--thread_max** - max number of threads to run concurrently, the default is 5
