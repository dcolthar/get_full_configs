# get and write the full config to a file
from napalm import get_network_driver
import os
import difflib
import hashlib
from datetime import datetime

def get_full_config(network_connection):
    '''
    Get the full config and write to a file named after the host
    :param network_connection:
    :param hostname:
    :return:
    '''
    base_folder = 'config_output'
    # is there an existing config, we leave as False or change later
    existing_config = False
    # current date formatted how we want
    today = datetime.now()
    today = today.strftime('%m_%d_%Y_%M_%S')
    # get config
    try:
        full_config = network_connection.get_config()

        # get hostname from facts
        facts = network_connection.get_facts()
        hostname = facts['hostname']

        # make a subfolder for each device
        base_folder = f'{base_folder}/{hostname}'
        try:
            os.makedirs(f'{base_folder}')
        except OSError as e:
            # the directory exists so no worries
            pass

        # name of the file to write to
        full_filename = f'{base_folder}/{hostname}_current_config.txt'

        # see if file exists
        if os.path.exists(full_filename):
            old_filename = full_filename
            full_filename = f'{base_folder}/{hostname}_CHANGED_config.txt'
            existing_config = True

        # write the most current config
        with open(full_filename, 'w') as f:
            f.write(full_config['startup'])

        # now lets do a diff on the files
        diff_output_file_name = f'{base_folder}/{hostname}_diff_output_{today}.txt'
        if existing_config:
            # get hashes of the contents of the config files
            old_file_hash = hashlib.md5(open(old_filename, 'rb').read()).hexdigest()
            new_file_hash = hashlib.md5(open(full_filename, 'rb').read()).hexdigest()
            # if the hashes don't match
            if old_file_hash != new_file_hash:
                print(f'there are differences between {full_filename} and {old_filename}, see {diff_output_file_name} for details')
                # get the configs into strings for comparison
                with open(old_filename, 'r') as f:
                    old_config = f.readlines()
                with open(full_filename, 'r') as f:
                    new_config = f.readlines()

                # open a file to write the differences
                with open(diff_output_file_name, 'w') as f:
                    # if there are differences...
                    for line in difflib.unified_diff(new_config, old_config, fromfile=old_filename, tofile=full_filename):
                        f.write(line)

                # now rename the files
                os.rename(old_filename, f'{base_folder}/{hostname}_OLD_CONFIG_RENAMED_{today}_config.txt')
                os.rename(full_filename, f'{base_folder}/{hostname}_current_config.txt')

            # if the file hashes match...nothing changes and we can delete the redundant config
            elif old_file_hash == new_file_hash:
                print(f'no changes to config file {full_filename}')
                os.remove(full_filename)

    except Exception as e:
        print(f'error occurred obtaining or writing the config for host {hostname}\n{e}')


