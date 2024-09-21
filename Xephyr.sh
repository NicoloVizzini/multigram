#!/bin/bash

# launch N Xephyr servers with ratpoison window manager
# Usage: Xephyr.sh N
# where N is the number of Xephyr servers to launch

# check that the first argument is a number
if [ -z "$1" ] || ! [[ "$1" =~ ^[0-9]+$ ]]; then
    echo "Usage: $0 <number of Xephyr servers>"
    exit 1
fi

N=$1

function launch_xephyr {
    D=":$1"
    echo "Launching Xephyr on display $D"
    Xephyr -br -ac -noreset -screen 900x900 $D &
    # wait until the Xephyr server is ready
    while ! xdpyinfo -display $D >/dev/null 2>&1; do
        sleep 0.1
    done
    ratpoison -d $D &
}

for i in $(seq 1 $N); do
    launch_xephyr $i
done

# wait for all Xephyr servers to exit, or until Ctrl+C is pressed
wait

# kill all background processes
kill $(jobs -p)

