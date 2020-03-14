#!/usr/bin/env bash

set -ex

cd /data/opa/
pytest --cov=. --cov=/opa-stack/examples/ $@ tests