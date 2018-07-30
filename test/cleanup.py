from parser import Parser
import logging
import os
import sys


class Cleanup(Parser):

    nodes = None

    def __init__(self, logger=None):
        Parser.__init__(self, logger)

    def run_cleanup(self):
        if self.nodes is None:
            logging.debug("node list is None")
            sys.exit(-1)

        # Should launch shell commands
        for i in range(0, len(self.nodes)):
            node = self.nodes[i]

            command = "ssh {0}@{1} \"killall -u {0}\" &".format(
                self.net_id, node.get_host_name())
            
            logging.debug(command)

            if os.system(command) != 0:
                logging.debug("Failed to execute %s", command)
                sys.exit( -1 )
           
            
if __name__ == "__main__":
    log_file_path = os.path.join(os.getcwd(), "cleanup.log")

    if os.path.isfile(log_file_path):
        os.remove(log_file_path)

    logging.basicConfig(
            filename="cleanup.log",
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%m-%d-%Y %I:%M %p',
            level=logging.DEBUG
    )

    clean = Cleanup(logging)

    logging.debug("Cleanup.py launched in " + os.getcwd())

    if os.path.isfile(os.path.join(os.getcwd(), clean.CONFIG_FILE)):
        logging.debug("Opened \'config.txt\'")
        clean.nodes = clean.parse_config_file()
        clean.run_cleanup()
        logging.debug("Completed")
    else:
        logging.warning("\'%s\' not found.", clean.CONFIG_FILE)
        print("Could not find \'{}\' in \' {}". \
            format(clean.CONFIG_FILE, os.getcwd()))
    logging.debug("Cleanup.py completed successfully. ")
    sys.exit(0)
