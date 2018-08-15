import argparse
import rpyc


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description='Called by mysql trigger to send events to the server')
    cli.add_argument('--state', help='State name')
    cli.add_argument('--machine', help='machine name')
    args = cli.parse_args()

    conn = rpyc.connect('localhost', port=1500)
    if args.state and args.machine:
        conn.root.put('{} {}', args.state, args.machine)
    else:
        conn.root.put(None)
