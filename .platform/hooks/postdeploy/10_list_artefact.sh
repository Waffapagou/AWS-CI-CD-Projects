.platform/hooks/postdeploy/10_list_artefact.sh
#!/bin/bash
set -e
ls -lah /var/app/current
ls -lah /var/app/current/artefact || true