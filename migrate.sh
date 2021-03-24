#!/usr/bin/env bash

for arg in "$@"
do
    case $arg in
        --mode)
        mode=$2
        ;;

        --message)
        message=$4
        ;;
    esac
done

export FLASK_APP=run.py
export FLASK_ENV=$mode

flask db migrate -m "$message"
flask db upgrade