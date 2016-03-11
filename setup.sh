#!/bin/bash

command_exists () {
    if command -v $1 >/dev/null 2>&1; then
        echo "$1 found.";
    else
        echo >&2 "$1 not found.";
        exit 1;
    fi
}

command_exists node
command_exists npm
command_exists bower

cd webapp/ && npm install
cd app/ && bower install
cd ../../

echo "webapp setup complete."

