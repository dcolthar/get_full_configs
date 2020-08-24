import napalm_common_operations
from getpass import getpass
import threading
from queue import Queue
import pandas as pd
import argparse
import os



class Main():

    def __init__(self):
        args = argparse.ArgumentParser()
        args.add_argument('--file_name', help='name of the file to pull hosts from default is host_list.xlsx',
                          default='host_list.xlsx')
        args.add_argument('--thread_max', help='number of worker threads to concurrently run default is 5', default=5),
        args.add_argument('--username', help='the username to use to connect to devices', default='admin')
        # parse all the arguments
        arguments = args.parse_args()
        # convert to a dictionary
        self.args_dict = vars(arguments)

        # kick off the threading
        self.do_thread()

        # at this point when control has returned here we want to make sure all work in queues is complete
        self.work_queue.join()


    def do_thread(self):
        # we need the password to use to connect
        password = getpass('Enter the password to use to connect to hosts:')
        # we'll store all our hosts in a queue eventually
        self.work_queue = Queue(maxsize=0)
        # open file to read in host list
        hosts = pd.read_excel(self.args_dict['file_name'])
        # iterate through and add all hosts to the queue
        for index, value in hosts.iterrows():
            self.work_queue.put(
                {
                    'host': value['IP Address'],
                    'device_type': value['Device Type']
                }
            )
        # now we kick off our threads
        for i in range(int(self.args_dict['thread_max'])):
            worker_thread = threading.Thread(
                target=self.do_work,
                name=f'worker_thread_number_{i}',
                kwargs={
                    'password': password
                }
            )
            # daemonize the thread
            worker_thread.setDaemon(True)
            # start the thread
            worker_thread.start()

    def do_work(self, password):
        # while our queue isn't empty
        while not self.work_queue.empty():
            try:
                # lets get our host info
                host_info = self.work_queue.get()
                print(f'beginning work on host at ip {host_info["host"]}')

                # lets try to connect
                network_connection = napalm_common_operations.connect_to_network_device(
                    host=host_info['host'],
                    username=self.args_dict['username'],
                    password=password,
                    device_type=host_info['device_type']
                )
                # if the connection failed...False was returned and we just skip this
                if network_connection:

                    # should we write the full config to a file
                    napalm_common_operations.get_full_config(network_connection=network_connection,)

                else:
                    print(f'completing work on host at ip {host_info["host"]} due to error')


                # disconnect from the network device
                napalm_common_operations.disconnect_from_network_device(network_connection=network_connection)
            except Exception as e:
                print(f'an Exception occurred while connecting\n{e}')
            finally:
                # signal queue entry work is done
                self.work_queue.task_done()

if __name__ == '__main__':
    main = Main()