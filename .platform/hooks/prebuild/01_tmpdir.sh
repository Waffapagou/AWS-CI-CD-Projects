#!/bin/bash
set -e
mkdir -p /var/tmp
chown root:root /var/tmp
chmod 1777 /var/tmp
export TMPDIR=/var/tmp
echo 'export TMPDIR=/var/tmp' > /etc/profile.d/eb_tmpdir.sh