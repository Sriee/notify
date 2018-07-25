import sys
from random import randint
from time import sleep


def publisher():
    state = ['ERROR', 'SUSPENDED', 'COMPLETED']
    machines = ['HIGH' + str(i) for i in range(10, 18)]
    print(state[randint(0, len(state) - 1)] + '-' + machines[randint(0, len(machines)
                                                                      - 1)],
          file=sys.stderr, flush=True)


def runner():
    print('Started Runner.')
    while True:
        try:
            publisher()
            sleep(5)
        except KeyboardInterrupt:
            print('Existing publisher')
            break


if __name__ == '__main__':
    runner()
