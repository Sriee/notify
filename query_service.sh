#!/bin/sh

workdir=/home/sriee/Git/query
workdir2=[/]home/sriee/Git/query/venv/bin/python
venv_home=${workdir}/venv/bin/python
controller=${workdir}/service/controller.py

start() {
    cd $workdir
    $venv_home $controller &
    echo "Controller Service Started."
}

stop() {
    pid=`ps -ef | grep "${workdir2} ${controller}" | awk '{print $2}'`
    kill $pid
    sleep 2
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
        echo "Usage: service/controller.py {start|stop|restart}"
        exit 1
esac
exit 0