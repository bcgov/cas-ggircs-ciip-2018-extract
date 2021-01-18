from jsonschema import validate
import json
from model.application import Application
from model.facility import Facility
from model.operator import Operator

from util import remove_key_from_dict

class FormBuilder:

  def validate_form(form, schema_file_name):
      with open(f'./json_schema/{schema_file_name}') as schema_file:
        schema = json.load(schema_file)
        validate(instance=form, schema=schema)


  def build_administration_form(operator: Operator, contact_info, facility: Facility, application: Application) -> dict:

    facility_data = {
      "bcghgid": facility.bcghg_id,
      "facilityName": facility.name,
      "facilityType": facility.type,
      "facilityDescription": facility.description
    }

    operator_data = {
      "name": operator.legal_name,
      "naics": facility.naics,
      "tradeName": operator.trade_name,
      "mailingAddress": {},
      "bcCorporateRegistryNumber": operator.bc_corp_reg,
      "isBcCorpRegNumberValid": operator.is_bc_cop_reg_valid,
      "orgBookLegalName": operator.orgbook_legal_name,
      "duns": operator.duns,
      "operationalRepresentative": contact_info['operational_representative_contact'],
      "certifyingOfficial": contact_info['certifying_official_contact']
    }

    app_metadata = {
      "sourceFileName": application.source_file_name,
      "sourceSHA1" : application.source_sha1,
      "importedAt" : application.imported_at,
      "applicationType" : application.application_type,
      "signatureDate" : application.signature_date
    }

    form = {
      "comments" : "CIIP 2018 admin import",
      "facility": facility_data,
      "operator": operator_data,
      "applicationMetadata": app_metadata
    }

    FormBuilder.validate_form(form, 'administration.json')

    return form

  def build_emission_form(emission_data):

    # Emission is a dictionary
    #    keys are the source type names
    #    values are lists of gases for that source type
    sourceTypes = []

    for sourceTypeName in emission_data:

      gases = emission_data[sourceTypeName]
      for g in gases:
        del g['sourceTypeName']

      sourceTypes.append(
        {
          "sourceTypeName": sourceTypeName,
          "gases" : gases
        }
      )

    form = {
      "comments": "CIIP 2018 emissions import",
      "sourceTypes": sourceTypes
    }

    FormBuilder.validate_form(form, 'emission.json')

    return form

  def build_fuel_form(fuel_data):

    form = []

    for fuel in fuel_data:
      form.append({
        "comments" : "",
        "fuelType" : fuel['fuel_type'],
        "fuelTypeAlt" : fuel['fuel_type_alt'],
        "fuelDescription" : fuel['fuel_description'],
        "quantity" : fuel['quantity'],
        "fuelUnits" : fuel['fuel_units'],
        "associatedEmissions" : fuel['carbon_emissions']
      })

    FormBuilder.validate_form(form, 'fuel.json')

    return form

  def build_production_form(production_data, energy_data):
    form = production_data + energy_data
    FormBuilder.validate_form(form, 'production.json')

    return form

