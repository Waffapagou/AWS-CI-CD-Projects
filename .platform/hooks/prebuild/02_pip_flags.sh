#!/bin/bash
set -e
export PIP_NO_CACHE_DIR=1
echo 'export PIP_NO_CACHE_DIR=1' > /etc/profile.d/eb_pip.sh
/usr/bin/pip3 install --upgrade pip setuptools wheel