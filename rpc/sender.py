import rpyc


if __name__ == '__main__':
    c = rpyc.connect('localhost', port=1500)
    conn = c.root

    for i in range(11, 20):
        conn.put('HIGH{}'.format(i))
