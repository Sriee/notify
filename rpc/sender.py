import argparse
import rpyc

# Configure service port and address here
SERVICE_ADDRESS = 'localhost'
SERVICE_PORT = 1600  # Configure service port here

if __name__ == '__main__':
    cli = argparse.ArgumentParser(description='Called by mysql trigger to send events to the server')
    cli.add_argument('--state', nargs=1, help='Machine State',
                     choices=['Completed', 'Error', 'Executing', 'Imaging', 'Pending', 'Suspended']
                     )
    cli.add_argument('--machine', nargs=1, help='Machine name',
                     choices=['As203', 'HIGH16', 'HIGH17', 'HIGH18', 'HIGH19', 'HIGH20', 'HIGH21', 'HIGH5', 'High6',
                              'MID32', 'MID33', 'MID4', 'MID5']
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
