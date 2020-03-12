#!/usr/bin/env bash

set -ex

/data/opa/scripts/test.sh

curl -s https://codecov.io/bash | bash