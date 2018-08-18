#!/bin/bash

workdir=/home/sriee/Git/query
server=${workdir}/service/server.py
trigger=${workdir}/service/trigger.py
venv_home=${workdir}/venv/bin/python

start() {
    echo "Starting Server"
    ${venv_home} ${server} &

    sleep 5
    echo "Starting Client"
    ${venv_home} launcher.py -n 1 start

    sleep 5
    echo "Starting trigger"
    ${venv_home} ${workdir}/service/trigger.py &
}

stop() {
    echo "Stopping Clients"
    ${venv_home} launcher.py stop

    pid=`ps -ef | grep "${workdir}/venv/bin/[p]ython ${server}" | awk '{print $2}'`
    echo "Stopping Server: ${pid}"
    kill ${pid}

    pid=`ps -ef | grep "${workdir}/venv/bin/[p]ython ${trigger}" | awk '{print $2}'`
    echo "Stopping trigger: ${pid}"
    kill ${pid}
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
