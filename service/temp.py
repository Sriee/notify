import argparse


if __name__ == '__main__':

    cli = argparse.ArgumentParser(description='Called by mysql trigger to send events to the server')
    cli.add_argument('--state', nargs=1, help='Machine State',
                     choices=['Completed', 'Error', 'Executing', 'Imaging', 'Pending', 'Suspended']
                     )
    cli.add_argument('--machine', nargs=1, help='Machine name',
                     choices=['High11', 'High12', 'High13', 'High14', 'High15', 'High16', 'High17', 'High18', 'High19', 
                              'High20', 'High21']
                     )
    cli.add_argument('--stop', action='store_true', help='Stop Trigger RPC service')

    args, conn = cli.parse_args(), None
    with open('temp.txt', 'a') as wp:
        wp.write('{} {} {}\n'.format(args.state[0], args.machine[0], args.stop))
    
