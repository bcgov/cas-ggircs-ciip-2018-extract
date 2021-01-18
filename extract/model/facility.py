
from .application import Application

class Facility:
  id = 0
  operator = None

  name = None
  bcghg_id = None
  type = None
  naics = None
  description = None
  swrs_facility_id = None
  production_calculation_explanation = None
  production_additional_info = None
  production_public_info = None

  ciip_db_id = None

  def __init__(self, operator):
    self.operator = operator
    return

  def save(self, cursor):
    cursor.execute(
        ('''
        insert into ciip_2018_load.facility
        (
            application_id, operator_id, facility_name, facility_type,
            bc_ghg_id, facility_description, naics, swrs_facility_id,
            production_calculation_explanation, production_additional_info,
            production_public_info
        )
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        returning id
        '''
        ),
        (
            self.application.id, # To remove
            self.operator.id,
            self.name,
            self.type,
            self.bcghg_id,
            self.description,
            self.naics,
            self.swrs_facility_id,
            self.production_calculation_explanation,
            self.production_additional_info,
            self.production_public_info
        )
    )
    self.id = cursor.fetchone()[0]
    return self.id
