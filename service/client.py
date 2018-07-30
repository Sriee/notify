import sys
import signal


def exit_handler(sig, stack):
    with open(sys.argv[0] + '.txt', 'a') as fp:
        fp.write('Exit handler called')
    sys.exit(0)


if __name__ == '__main__':
    del sys.argv[0]
    signal.signal(signal.SIGTERM, exit_handler)

    with open(sys.argv[0] + '.txt', 'w') as wp:
        wp.write('{} will start at {}:{}\n'.format(*sys.argv))
    while True:
        pass
