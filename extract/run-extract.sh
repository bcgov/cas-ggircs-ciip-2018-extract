#!/bin/bash

# This script executes the extract python script
# It is intended to be executed in an openshift container having the variables used below defined

python ./extract.py --bucket $BUCKET_NAME --dir $BUCKET_PATH --host $PGHOST --db $PGDATABASE --user $PGUSER --password $PGPASSWORD && exit 0
