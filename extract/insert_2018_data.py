from model.facility import Facility
import json
from create_json_schema_rows import create_2018_json_schema_forms
from create_reporting_year import create_2018_reporting_year
from form_builder import FormBuilder
import util
from util import get_sheet_value, none_if_not_number

def modify_triggers(cursor, action):
    # disable CIIP db triggers
    cursor.execute(
        '''
        do $$
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
          end
        $$;
        ''',
        (action)
    )

def validate_schema(form_result):
    # validate form_result data with form_json schema

def find_or_create_operator(operator):
    # Get id of operator in CIIP db || create operator in CIIP db
    # CIIP db id & all operator info
    cursor.execute(
        '''
        select id from ggircs_portal.organisation where swrs_organisation_id = %d;
        ''',
        (operator['swrs_operator_id'])
    )
    res = cursor.fetchone()
    if res in not None:
        operator['ciip_db_id'] = res[0]
    else:
        cursor.execute(
            '''
            insert into ggircs_portal.organisation(reporting_year, operator_name, operator_trade_name, duns)
            values (%d, %s, %s, %s) returning id;
            ''',
            (2018, operator['legal_name'], operator['trade_name'], operator['duns'])
        )
        # Get ID of newly created row & save to operator object
        res = cursor.fetchone()
        operator['ciip_db_id'] = res[0]

def find_or_create_facility(operator, facility):
    # Get id of facility in CIIP db || create facility in CIIP db
    # Check that the organisation_id in CIIP db = id from find_or_create_operator
    # CIIP db id & all fac info

    cursor.execute(
        '''
        select id, organisation_id from ggircs_portal.facility where swrs_facility_id = %d;
        ''',
        (facility['swrs_facility_id'])
    )
    res = cursor.fetchone()
    if res is not None:
        if operator.ciip_db_id != res[1]:
            raise exception('Operator ID mismatch. swrs_facility_id: {res[0]}')
        else:
            facility['ciip_db_id'] = res[0]
    else:
        cursor.execute(
            '''
            insert into ggircs_portal.facility(organisation_id, facility_name, facility_type, bcghgid)
            values (%d, %s, %s, %s) returning id;
            ''',
            (operator['ciip_db_id'], facility['name'], facility['type'], facility['bcghg_id'])
        )
        # Get ID of newly created row & save to facility object
        res = cursor.fetchone()
        facility['ciip_db_id'] = res[0]

def create_application(facility, application):
    # Fully manual, create: application, application_revision, application_revision_status='approved', form_result, form_result_status='approved' X ?
    # Create row in ggircs_portal.application
    cursor.execute(
        '''
        insert into ggircs_portal.application(facility_id, reporting_year)
        values (%d, %d) returning id;
        ''',
        (facility['ciip_db_id'], 2018)
    )
    res = cursor.fetchone()
    app_id = res[0]
    # Create row in ggircs_portal.application_revision
    cursor.execute(
        '''
        insert into ggircs_portal.application_revision(application_id, version_number, legal_disclaimer_accepted, created_at)
        values (%d, %d, %s, %s);
        ''',
        (app_id, 1, 't', '2019-07-01 00:00:00-07')
    )
    # Create row in ggircs_portal.application_revision_status
    cursor.execute(
        '''
        insert into ggircs_portal.application_revision_status(application_id, version_number, application_revision_status, created_at)
        values (%d, %d, %s, %s);
        ''',
        (app_id, 1, 'approved', '2019-07-01 00:00:00-07')
    )
    # Create rows in ggircs_portal.form_result & form_result_status for each new form_json schema
    slugs = ['admin-2018', 'emission-2018', 'fuel-2018', 'production-2018']
    for i in slugs:
        cursor.execute(
            '''
            select id from ggircs_portal.form_json where slug=%s;
            ''',
            (i)
        )
        res = cursor.fetchone();
        form_id = res[0]
        # Create form_result row
        cursor.execute(
            '''
            insert into ggircs_portal.form_result(form_id, application_id, version_number, form_result, created_at)
            values (%d, %d, %d, %s, %s)
            ''',
            (form_id, app_id, 1, '\{\}', '2019-07-01 00:00:00-07')
        )
        # Create form_result_status row
        cursor.execute(
            '''
            insert into ggircs_portal.form_result_status(form_id, application_id, version_number, form_result_status, created_at)
            values (%d, %d, %d, %s, %s)
            ''',
            (form_id, app_id, 1, 'approved', '2019-07-01 00:00:00-07')
        )
    return app_id


def populate_form_results(application, facility, operator, contact, fuel, emission, production, energy, application_id):
    # Parse data from these objects into form_result table with appropriate form_id
    # Admin form
    admin_form = FormBuilder.build_administration_form(operator, contact, facility, application)
    cursor.execute(
        '''
        update ggircs_portal.form_result set form_result=%s
        where application_id=%d
        and version_number=1
        and form_id = (select id from ggircs_portal.form_json where slug='admin-2018');
        ''',
        (json.dumps(admin_form), application_id)
    )
    # Emission form
    emission_form = FormBuilder.build_emission_form(emission)
    cursor.execute(
        '''
        update ggircs_portal.form_result set form_result=%s
        where application_id=%d
        and version_number=1
        and form_id = (select id from ggircs_portal.form_json where slug='emission-2018');
        ''',
        (json.dumps(emission_form), application_id)
    )
    # Fuel form
    fuel_form = FormBuilder.build_fuel_form(fuel)
    cursor.execute(
        '''
        update ggircs_portal.form_result set form_result=%s
        where application_id=%d
        and version_number=1
        and form_id = (select id from ggircs_portal.form_json where slug='fuel-2018');
        ''',
        (json.dumps(fuel_form), application_id)
    )
    # Production form
    prod_form = FormBuilder.build_production_form(production, energy)
    cursor.execute(
        '''
        update ggircs_portal.form_result set form_result=%s
        where application_id=%d
        and version_number=1
        and form_id = (select id from ggircs_portal.form_json where slug='production-2018');
        ''',
        (json.dumps(prod_form), application_id)
    )

def insert_data(cursor, operator, facility, application, contact, fuel, emission, production, energy):
    modify_triggers('disable')

    find_or_create_operator(operator, application)
    find_or_create_facility(operator, facility)
    application_id = create_application(facility, application)
    populate_form_results(application, facility, operator, contact, fuel, emission, production, energy, application_id)

    modify_triggers('enable')
