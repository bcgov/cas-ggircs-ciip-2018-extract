from model.facility import Facility
import util
from util import get_sheet_value, none_if_not_number


def modify_triggers(cursor, action):
    # disable CIIP db triggers
    cursor.execute(
        '''
        $do$
          declare table_name text;
          declare table_trigger text;
          declare alter_statement text;
          begin

            for table_name, table_trigger in
              select event_object_table as table_name, trigger_name as table_trigger
              from information_schema.triggers
              where event_object_schema='ggircs_portal'
              order by table_name asc

            loop
              alter_statement:=concat('alter table ggircs_portal.', table_name, ' ', %s, ' trigger ', table_trigger);
              execute alter_statement;
            end loop;
          end;

        $do$
        select distinct swrs_facility_id from swrs.identifier
        where identifier_value = %s
        ''',
        (action)
    )


def validate_schema(form_result):
    # validate form_result data with form_json schema

def reconcile_operator(operator):
    # Get id of operator in CIIP db || create operator in CIIP db
    # CIIP db id & all operator info
    cursor.execute(
        '''
        select id from ggircs_portal.organisation where swrs_organisation_id = %d;
        ''',
        (operator['swrs_operator_id'])
    )
    res = cursor.fetchone()
    operator['ciip_db_id'] = res[0]


def reconcile_facility(operator, facility):
    # Get id of facility in CIIP db || create facility in CIIP db
    # Check that the organisation_id in CIIP db = id from reconcile_operator
    # CIIP db id & all fac info

    cursor.execute(
        '''
        select id, organisation_id from ggircs_portal.facility where swrs_facility_id = %d;
        ''',
        (facility['swrs_facility_id'])
    )
    res = cursor.fetchone()
    if operator.ciip_db_id != res[1]:
        raise exception('Operator ID mismatch. swrs_facility_id: {res[0]}')
    else:
        facility['ciip_db_id'] = res[0]

def create_application(facility, application):
    # Fully manual, create: application, application_revision, application_revision_status='approved', form_result, form_result_status='approved' X ?
    cursor.execute(insert blah blah application)
    ...
    validate_schema()

def populate_form_results(application, facility, operator, contact, fuel, emission, production, energy, equipment):
    # Parse data from these objects into form_result table with appropriate form_id

    # insert into ggircs_portal.form_result(admin info: application, facility, operator, contact)
    # insert into ggircs_portal.form_result(fuel info: fuel)
    # insert into ggircs_portal.form_result(emission info: emission)
    # insert into ggircs_portal.form_result(prod info: production, energy)
    # equipment?


def insert_data(cursor, operator, facility, application, contact, fuel, emission, production, energy, equipment):
    modify_triggers('disable')
    operator_details = reconcile_operator(operator, application)
    facility_details = reconcile_facility(operator_details, facility)
    application_details = create_application(facility_details, application)
    modify_triggers('enable')
