import datetime

class Application:
  facility = None
  source_file_name = ""
  source_sha1 = ""
  imported_at = None
  application_year = 2018
  application_type = ""
  signature_date = None
  id = 0

  def __init__(self, facility, source_file_name, source_sha1, imported_at, application_year, application_type, signature_date):
    if application_year != 2018:
      raise ValueError(f'Application year should always be 2018, but was {application_year} in {source_file_name}')

    self.facility = facility

    self.source_file_name = source_file_name
    self.source_sha1 = source_sha1
    self.imported_at = imported_at
    self.application_year = application_year
    self.application_type = application_type
    self.signature_date = signature_date
    return
