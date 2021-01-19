import os
import xlrd
import argparse
import json
from google.cloud import storage
import extract_application
import extract_operator
import extract_facility
import extract_contact_info
import extract_production
import extract_equipment
import extract_energy
import extract_fuel
import extract_emission
from create_reporting_year import create_2018_reporting_year
from create_json_schema_rows import create_2018_json_schema_forms
from insert_2018_data import insert_data
import psycopg2


# The env variable GOOGLE_APPLICATION_CREDENTIALS needs to point at a json file with the gcs credentials
# "gs://ciip-2018/CIIP applications_2018/CIIP data_final"
def list_files_in_bucket(bucket_name, prefix):
    storage_client = storage.Client()
    def generate_gcs_url(blob): return f'gs://{bucket_name}/{blob.name}'
    return list(map(generate_gcs_url, storage_client.list_blobs(bucket_name, prefix=prefix)))

def list_blobs_in_bucket(bucket_name, prefix):
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
    return list(blobs)

def extract_book(blob, cursor):
    if not os.path.exists('./tmp'):
        os.makedirs('./tmp')
    fileName = './tmp/' + blob.name.replace("/", "_")

    if not os.path.exists(fileName):
        blob.download_to_filename(fileName)

    try:
        ciip_book = xlrd.open_workbook(fileName)
    except xlrd.biffh.XLRDError:
        print('skipping file ' + blob.name)
        return

    operator = extract_operator.extract(ciip_book, cursor)
    facility = extract_facility.extract(ciip_book, cursor, operator)
    application = extract_application.extract(ciip_book, fileName, facility)

    contact_info = extract_contact_info.extract(ciip_book)
    fuel = extract_fuel.extract(ciip_book)
    energy_products = extract_energy.extract(ciip_book)
    products = extract_production.extract(ciip_book)
    emissions = extract_emission.extract(ciip_book)

    insert_data(cursor, operator, facility, application, contact_info, fuel, emissions, products, energy_products)

    return

parser = argparse.ArgumentParser(description='Extracts data from CIIP excel application files and writes it to database')
parser.add_argument('--db', default='ciip')
parser.add_argument('--host', default='localhost')
parser.add_argument('--user')
parser.add_argument('--password')
parser.add_argument('--bucket')
parser.add_argument('--dir')
args = parser.parse_args()

conn = psycopg2.connect(dbname=args.db, host=args.host, user=args.user, password=args.password)
cur = conn.cursor()

gcs_blobs = list_blobs_in_bucket(args.bucket, args.dir)

try:
    create_2018_reporting_year(cur)
    create_2018_json_schema_forms(cur)

    for blob in gcs_blobs:
        print('parsing: ' + blob.name)
        extract_book(blob, cur)

    conn.commit()
except Exception as e:
    conn.rollback()
    raise e
finally:
    cur.close()
    conn.close()
