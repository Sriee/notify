import argparse
import rpyc

# Configure service port and address here
SERVICE_ADDRESS = 'localhost'
SERVICE_PORT = 2100


if __name__ == '__main__':

    cli = argparse.ArgumentParser(description='Called by mysql trigger to send events '
                                              'to the server')
    cli.add_argument('--state', nargs=1, help='Machine State',
                     choices=['Pending', 'Configuration', 'Executing', 'Error',
                              'Completed', 'Suspended']
                     )
    cli.add_argument('--machine', nargs=1, help='Machine name',
                     choices=['Machine1', 'Machine2', 'Machine3', 'Machine4',
                              'Machine5', 'Machine6', 'Machine7', 'Machine8',
                              'Machine9', 'Machine10']
                     )
    cli.add_argument('--stop', action='store_true', help='Stop Trigger RPC service')

    args, conn = cli.parse_args(), None

    try:
        conn = rpyc.connect(SERVICE_ADDRESS, port=SERVICE_PORT)
        if args.state and args.machine:
            conn.root.put(state=args.state[0], machine=args.machine[0])
        else:
            conn.root.put(stop=True)
    finally:
        conn.close()
