
from extract.model.application import Application
from extract.model.facility import Facility
from extract.model.operator import Operator

from .util import remove_key_from_dict

class FormBuilder:

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

    return form

  def build_emission_form(emission_data):

    # Emission is a dictionary 
    #    keys are the source type names
    #    values are lists of gases for that source type
    sourceTypes = []

    for sourceTypeName in emission_data:
      
      sourceTypes.append(
        {
          "sourceTypeName": sourceTypeName,
          "gases" : list(map(lambda gas_data : remove_key_from_dict(gas_data, 'sourceTypeName'), emission_data[sourceTypeName]))
        }
      )

    form = {
      "comments": "CIIP 2018 emissions import",
      "sourceTypes": sourceTypes
    }

    return form

  def build_fuel_form(fuel_data):

    form = []

    for fuel in fuel_data:
      form.append({
        "comments" : "",
        "fuelType" : fuel.fuel_type,
        "fuelTypeAlt" : fuel.fuel_type_alt,
        "fuelDescription" : fuel.fuel_description,
        "quantity" : fuel.quantity,
        "fuelUnits" : fuel.fuel_units,
        "associatedEmissions" : fuel.carbon_emissions
      })

    return form

  def build_production_form(production_data, energy_data):

    return production_data + energy_data

  