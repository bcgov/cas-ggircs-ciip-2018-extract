#!/bin/bash

# This script executes the extract python script
# It is intended to be executed in an openshift container having the variables used below defined

python ./extract.py --dir "$CIIP_FILES_DIR" --host $PGHOST --db $PGDATABASE --user $PGUSER --password $PGPASSWORD && echo 'extraction done'
