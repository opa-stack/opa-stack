#!/usr/bin/env bash

set -ex

/data/opa/scripts/test.sh

# bash <(curl -s https://codecov.io/bash) -y /data/opa/tests/codecov.yml

bash <(curl -s https://codecov.io/bash) -k /api/data/opa/