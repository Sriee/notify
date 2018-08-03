#!/bin/bash

workdir=/home/sriee/Git/query
server=${workdir}/service/server.py
venv_home=${workdir}/venv/bin/python

start() {
    echo "Starting Server"
    $venv_home $server &

    # $venv_home launcher.py -n 5 start
    sleep 5
    echo "Starting Client 1"
    $venv_home ${workdir}/service/client.py --name Client-1 --sub Pending &

    sleep 5
    echo "Starting Client 2"
    $venv_home ${workdir}/service/client.py --name Client-2 --sub Error &

    sleep 5
    echo "Starting Client 3"
    $venv_home ${workdir}/service/client.py --name Client-3 --sub Suspended &

}

stop() {
    echo "Stopping Clients"
    $venv_home launcher.py stop

    echo "Stopping Server"
    pid=`ps -ef | grep "${workdir}/venv/bin/[p]ython ${server}" | awk '{print $2}'`
    kill $pid
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        start
        ;;
    *)
        echo
        echo "Usage: ./service.sh { start | stop | restart }"
        echo
        exit 1
esac
exit 0
