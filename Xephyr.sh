#!/bin/bash

# check that the first argument is a valid DISPLAY such as :1, :2, etc.
if [ -z "$1" ] || ! [[ "$1" =~ ^:[0-9]+$ ]]; then
    echo "Usage: $0 :<display number>"
    exit 1
fi

export D=$1

Xephyr -br -ac -noreset -screen 900x900 $D &
# wait until the Xephyr server is ready
while ! xdpyinfo -display $D >/dev/null 2>&1; do
    sleep 0.1
done

ratpoison -d $D &

# wait until the Xephyr server is closed
wait %1


