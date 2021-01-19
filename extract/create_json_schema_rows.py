import json
from jsonschema import validate

def load_json_form(path):
  with open(path) as json_file:
    # We just try to load the file in a JSON object
    json_form = json.load(json_file)
    return json.dumps(json_form)


def insert(cursor, data, unique_slug):
  cursor.execute(
      '''
      select slug from ggircs_portal.form_json where slug = %s;
      ''',
      (unique_slug)
  )
  res = cursor.fetchone()
  if res is None:
      statement = """
        insert into ggircs_portal.form_json (name, slug, short_name, description, form_json, prepopulate_from_ciip, prepopulate_from_swrs, created_at)
        values (%s,%s,%s,%s,%s,false,false,now())
      """
      cursor.execute((statement), data)


def create_2018_json_schema_forms(cursor):

  # Admin form
  admin_json_form = load_json_form("./json_schema/administration.json")
  admin_data = (
    "2018 Administration Data",
    "admin-2018",
    "2018 Admin",
    "Admin form for CIIP 2018",
    admin_json_form
  )
  insert(cursor, admin_data, 'admin-2018')

  # Emission form
  emission_json_form = load_json_form("./json_schema/emission.json")
  emission_data = (
    "2018 Emission",
    "emission-2018",
    "2018 Emission",
    "Emission form for CIIP 2018",
    emission_json_form
  )
  insert(cursor, emission_data, 'emission-2018')

  # Fuel form
  fuel_json_form = load_json_form("./json_schema/fuel.json")
  fuel_data = (
    "2018 Fuel",
    "fuel-2018",
    "2018 Fuel",
    "Fuel form for CIIP 2018",
    fuel_json_form
  )
  insert(cursor, fuel_data, 'fuel-2018')

  # Production form# Fuel form
  production_json_form = load_json_form("./json_schema/production.json")
  production_data = (
    "2018 Production",
    "production-2018",
    "2018 Production",
    "Production form for CIIP 2018",
    production_json_form
  )
  insert(cursor, production_data, 'production-2018')
