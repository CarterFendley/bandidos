#!/bin/bash -e

cd $(dirname $0)

python3 -m pytest "$@"
