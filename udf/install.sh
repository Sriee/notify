#!/usr/bin/env bash

echo "Compiling MySQL UDF"
echo

# Remove existing shared object and create a new one
if [ -e /usr/lib/mysql/plugin/libudf.so ]; then
    make clean
fi

make

if test $? -ne 0; then
    echo
    echo "MySQL UDF compilation failed. Probable causes:"
    echo "  1. Permission issues"
    echo "  2. Missing libmysqlclient-dev package"
    exit 1
else
    echo
    echo "Compilation successful."
fi
