

def create_2018_reporting_year(cursor):
  statement = """
      insert into ggircs_portal.reporting_year (
        reporting_year, 
        reporting_period_start, 
        reporting_period_end, swrs_deadline, 
        application_open_time, 
        application_close_time
      )
      values (
        2018, 
        '2018-01-01 00:00:00.0-08', 
        '2018-12-31 23:59:59.0-08', 
        '2019-06-01 00:00:00.000000-07', 
        '2019-04-01 14:49:54.191757-07', 
        '2019-12-30 14:49:54.191757-08'
      )
      on conflict(reporting_year) do nothing"""
  # On conflict, we use the existing 2018 year of the system

  cursor.execute(statement)
