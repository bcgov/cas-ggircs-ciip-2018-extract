from model.facility import Facility
import util
from util import get_sheet_value, none_if_not_number


def modify_triggers(disable):
    # disable CIIP db triggers

def validate_schema(form_result):
    # validate form_result data with form_json schema

def reconcile_operator(operator, application):
    # Get id of operator in CIIP db || create operator in CIIP db
    # CIIP db id & all operator info

def reconcile_facility(operator, facility):
    # Get id of facility in CIIP db || create facility in CIIP db
    # Check that the organisation_id in CIIP db = id from reconcile_operator
    # CIIP db id & all fac info

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
    modify_triggers(True)
    operator_details = reconcile_operator(operator, application)
    facility_details = reconcile_facility(operator_details, facility)
    application_details = create_application(facility_details, application)
    modify_triggers(False)
