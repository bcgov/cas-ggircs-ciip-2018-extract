import json
from create_json_schema_rows import create_2018_json_schema_forms
from create_reporting_year import create_2018_reporting_year
from form_builder import FormBuilder

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
        (action,)
    )

def find_or_create_operator(cursor, operator):
    # Get id of operator in CIIP db || create operator in CIIP db
    # CIIP db id & all operator info
    cursor.execute(
        '''
        select id from ggircs_portal.organisation where swrs_organisation_id = %s;
        ''',
        (operator.swrs_operator_id,)
    )
    res = cursor.fetchone()
    if res is not None:
        operator['ciip_db_id'] = res[0]
    else:
        # Let's see if we have a 2018 insert of this org already
        cursor.execute(
            '''
            select id from ggircs_portal.organisation
            where reporting_year=%s
            and (
                operator_name=%s
                or operator_trade_name=%s
                or duns=%s
                )
            ''',
            (2018, operator.legal_name, operator.trade_name, operator.duns,)
        )

        # If no matching org, we insert
        if cursor.fetchone()[0] is None:
            cursor.execute(
                '''
                insert into ggircs_portal.organisation(reporting_year, operator_name, operator_trade_name, duns)
                values (%s, %s, %s, %s) returning id;
                ''',
                (2018, operator.legal_name, operator.trade_name, operator.duns)
            )
            # Get ID of newly created row & save to operator object
            res = cursor.fetchone()
            operator.ciip_db_id = res[0]

def find_or_create_facility(cursor, operator, facility):
    # Get id of facility in CIIP db || create facility in CIIP db
    # Check that the organisation_id in CIIP db = id from find_or_create_operator
    # CIIP db id & all fac info

    cursor.execute(
        '''
        select id, organisation_id from ggircs_portal.facility where swrs_facility_id = %s;
        ''',
        (facility.swrs_facility_id,)
    )
    res = cursor.fetchone()
    if res is not None:
        if operator.ciip_db_id != res[1]:
            raise exception('Operator ID mismatch. swrs_facility_id: {res[0]}')
        else:
            facility.ciip_db_id = res[0]
    else:

        cursor.execute(
            '''
            select id from ggircs_portal.facility
            where organisation_id=%s
            and facility_name=%s
            and facility_type=%s
            and bcghgid=%s
            ''',
            (operator.ciip_db_id, facility.name, facility.type, facility.bcghg_id)
        )
        res = cursor.fetchone()
        if res is None:
            cursor.execute(
                '''
                insert into ggircs_portal.facility(organisation_id, facility_name, facility_type, bcghgid)
                values (%s, %s, %s, %s) returning id;
                ''',
                (operator.ciip_db_id, facility.name, facility.type, facility.bcghg_id)
            )
            # Get ID of newly created row & save to facility object
            res = cursor.fetchone()
            facility.ciip_db_id = res[0]

def create_application(cursor, facility, application):
    # Fully manual, create: application, application_revision, application_revision_status='approved', form_result, form_result_status='approved' X ?
    # Create row in ggircs_portal.application
    cursor.execute(
        '''
        insert into ggircs_portal.application(facility_id, reporting_year)
        values (%s, %s) returning id;
        ''',
        (facility.ciip_db_id, 2018)
    )
    res = cursor.fetchone()
    app_id = res[0]
    # Create row in ggircs_portal.application_revision
    cursor.execute(
        '''
        insert into ggircs_portal.application_revision(application_id, version_number, legal_disclaimer_accepted, created_at)
        values (%s, %s, %s, %s);
        ''',
        (app_id, 1, 't', '2019-07-01 00:00:00-07')
    )
    # Create row in ggircs_portal.application_revision_status
    cursor.execute(
        '''
        insert into ggircs_portal.application_revision_status(application_id, version_number, application_revision_status, created_at)
        values (%s, %s, %s, %s);
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
            (i,)
        )
        res = cursor.fetchone()
        if res is None:
            print(slugs)
            print(i)
            print(res)
        form_id = res[0]
        # Create form_result row
        cursor.execute(
            '''
            insert into ggircs_portal.form_result(form_id, application_id, version_number, form_result, created_at)
            values (%s, %s, %s, %s, %s)
            ''',
            (form_id, app_id, 1, '{}', '2019-07-01 00:00:00-07')
        )
        # Create form_result_status row
        cursor.execute(
            '''
            insert into ggircs_portal.form_result_status(form_id, application_id, form_result_status, created_at)
            values (%s, %s, %s, %s)
            ''',
            (form_id, app_id, 'approved', '2019-07-01 00:00:00-07')
        )
    return app_id


def populate_form_results(cursor, application, facility, operator, contact, fuel, emission, production, energy, application_id):
    # Parse data from these objects into form_result table with appropriate form_id
    # Admin form
    admin_form = FormBuilder.build_administration_form(operator, contact, facility, application)
    cursor.execute(
        '''
        update ggircs_portal.form_result set form_result=%s, updated_at='2019-07-01 00:00:00-07'
        where application_id=%s
        and version_number=1
        and form_id = (select id from ggircs_portal.form_json where slug='admin-2018');
        ''',
        (json.dumps(admin_form, default=str), application_id)
    )
    # Emission form
    emission_form = FormBuilder.build_emission_form(emission)
    cursor.execute(
        '''
        update ggircs_portal.form_result set form_result=%s, updated_at='2019-07-01 00:00:00-07'
        where application_id=%s
        and version_number=1
        and form_id = (select id from ggircs_portal.form_json where slug='emission-2018');
        ''',
        (json.dumps(emission_form), application_id)
    )
    # Fuel form
    fuel_form = FormBuilder.build_fuel_form(fuel)
    cursor.execute(
        '''
        update ggircs_portal.form_result set form_result=%s, updated_at='2019-07-01 00:00:00-07'
        where application_id=%s
        and version_number=1
        and form_id = (select id from ggircs_portal.form_json where slug='fuel-2018');
        ''',
        (json.dumps(fuel_form), application_id)
    )
    # Production form
    prod_form = FormBuilder.build_production_form(production, energy)
    cursor.execute(
        '''
        update ggircs_portal.form_result set form_result=%s, updated_at='2019-07-01 00:00:00-07'
        where application_id=%s
        and version_number=1
        and form_id = (select id from ggircs_portal.form_json where slug='production-2018');
        ''',
        (json.dumps(prod_form), application_id)
    )

def insert_data(cursor, operator, facility, application, contact, fuel, emission, production, energy):
    modify_triggers(cursor, 'disable')

    find_or_create_operator(cursor, operator)
    find_or_create_facility(cursor, operator, facility)
    application_id = create_application(cursor, facility, application)
    populate_form_results(cursor, application, facility, operator, contact, fuel, emission, production, energy, application_id)

    modify_triggers(cursor, 'enable')
