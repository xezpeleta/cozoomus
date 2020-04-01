#! /usr/bin/env bash

COZOOMUS="/usr/src/app/cozoomus.py"
TIME=${SLEEP:=600}

function daemonize() {
    while true;
    do
        header
        run
        sleep $TIME
    done
}

function run() {
    python $COZOOMUS
}

function header() {
    echo -e "\n\n"
    echo "###############################################"
    echo "#                 COZOOMUS                    #"
    echo "###############################################"
    echo "# $(date)"
}

if [ -z "$ZOOM_API_KEY" ] || [ -z "$ZOOM_API_SECRET" ]; then
    echo "ERROR: required environment variables not defined"
    echo "- ZOOM_API_KEY"
    echo "- ZOOM_API_SECRET"
    exit 1
fi

if [ -n "$DAEMON" ]; then
    if [ "$DAEMON" == "true" ]; then
        echo "DAEMON mode enabled"
        daemonize
    else
        run
    fi
else
    run
fi
