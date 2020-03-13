#!/usr/bin/env bash

set -ex

cd /data/opa/
pytest --cov=. $@ tests