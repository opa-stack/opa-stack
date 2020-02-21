#!/bin/bash

build_deps="gcc make redhat-rpm-config platform-python-devel"

dnf install -y ${build_deps}
pip3 install -r /build/requirements.txt
dnf remove -y ${build_deps}