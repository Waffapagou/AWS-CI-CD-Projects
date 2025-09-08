#!/bin/bash
set -e
rm -rf /root/.cache/pip || true
rm -rf /var/app/staging/.cache || true
rm -rf /var/tmp/pip-* /tmp/pip-* || true