#!/usr/bin/env bash

set -ex

pytest --cov=. ${@}