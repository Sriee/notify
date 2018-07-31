#!/bin/bash

workdir=/home/sriee/Git/query
server=${workdir}/service/server.py
venv_home=${workdir}/venv/bin/python

start() {
    # cd $workdir

    echo "Starting Server"
    $venv_home $server &

    echo "Starting Clients"
    $venv_home launcher.py -n 1 start
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
        echo "Usage: service/controller.py { start | stop | restart }"
        echo
        exit 1
esac
exit 0
