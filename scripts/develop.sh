#!/usr/bin/env bash

for arg in "$@"
do
    case $arg in
        --production)
        mode=production
        ;;

        --development)
        mode=development
        ;;
    esac
done

export FLASK_APP=run.py
export FLASK_ENV=$mode

flask run