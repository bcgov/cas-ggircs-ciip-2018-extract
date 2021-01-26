def insert(cursor, data, unique_slug):
  # Idempotence check: if a row exists in ciip_application_wizard matching the unique_slug do not create it
  cursor.execute(
      '''
      select form_id from ggircs_portal.ciip_application_wizard caw join ggircs_portal.form_json fj on caw.form_id=fj.id and fj.slug = %s;
      ''',
      (unique_slug,)
  )
  res = cursor.fetchone()
  if res is None:
      statement = """
        insert into ggircs_portal.ciip_application_wizard (form_id, form_position, is_active)
        values ((select id from ggircs_portal.form_json where slug=%s), %s, false)
      """
      cursor.execute((statement), data)


def create_2018_wizard_rows(cursor):

  # Admin form
  admin_data = (
    "admin-2018",
    0
  )
  insert(cursor, admin_data, 'admin-2018')

  # Emission form
  emission_data = (
    "emission-2018",
    1
  )
  insert(cursor, emission_data, 'emission-2018')

  # Admin form
  fuel_data = (
    "fuel-2018",
    2
  )
  insert(cursor, fuel_data, 'fuel-2018')

  # Admin form
  production_data = (
    "production-2018",
    3
  )
  insert(cursor, production_data, 'production-2018')
