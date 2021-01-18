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
