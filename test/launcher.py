from parser import Parser
import logging
import os
import sys
import time


class Launcher(Parser):

    
    nodes = None

    def __init__(self, logger):
        Parser.__init__(self, logger)

    def run_command(self):
        # Change file path where AOS_Project.jar file is present
        filePath = "/home/011/s/sx/sxa156930/CS6378/"
        if self.nodes is None:
            logging.debug("node list is None")
            print("Parsing <id><host><port> failed")
            sys.exit(-1)

        # Should launch shell commands
        for i in range(0, len(self.nodes)):
            node = self.nodes[i]
            
            command = "ssh {0}@{1} \"cd {2};java -jar {3}{4} {5} >> Out_{5}.out\" &".format(
                self.net_id, node.get_host_name(), filePath, self.PROJ_NAME, self.PROJ_EXT, node.get_id())
            
            logging.debug(command)
            time.sleep(2)
            if os.system(command) != 0:
                logging.debug("Failed to execute %s", command)
                sys.exit( -1 )

if __name__ == "__main__":
    log_file_path = os.path.join(os.getcwd(), "launcher.log")

    if os.path.isfile(log_file_path):
        os.remove(log_file_path)

    logging.basicConfig(
            filename="launcher.log",
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%m-%d-%Y %I:%M %p',
            level=logging.DEBUG
    )

    launch = Launcher(logging)
    logging.debug("Launcher.py launched in " + os.getcwd())
    if os.path.isfile(os.path.join(os.getcwd(), launch.CONFIG_FILE)):
        logging.debug("Opened \'config.txt\'")
        launch.nodes = launch.parse_config_file()
        launch.run_command()
    else:
        logging.warning("\'%s\' not found.", launch.CONFIG_FILE)
        print("Could not find \'{}\' in \' {}". \
            format(launch.CONFIG_FILE, os.getcwd()))
    logging.debug("Launcher.py execution completed.")
