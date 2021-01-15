import datetime

class Application:
  source_file_name = ""
  source_sha1 = ""
  imported_at = None
  application_year = 2018
  application_type = ""
  signature_date = None
  id = 0

  def __init__(self, source_file_name, source_sha1, imported_at, application_year, application_type, signature_date):
    if application_year != 2018:
      raise ValueError(f'Application year should always be 2018, but was {application_year} in {source_file_name}')

    self.source_file_name = source_file_name
    self.source_sha1 = source_sha1
    self.imported_at = imported_at
    self.application_year = application_year
    self.application_type = application_type
    self.signature_date = signature_date
    return

  def to_json(self):
    return "{}"

  # Returns the id of the Application record that was created in the database
  # NB: Calling this multiple times will create multiple applications
  def save(self, cursor):
    cursor.execute( 
        (
          'insert into ciip_2018_load.application '
          '(source_file_name, source_sha1, imported_at, application_year, application_type, signature_date) '
          'values (%s, %s, %s, %s, %s, %s) '
          'returning id'        ),
        (
            self.source_file_name, self.source_sha1, self.imported_at, self.application_year, self.application_type, self.signature_date
        )
    )
    self.id = cursor.fetchone()[0]
    return self.id
