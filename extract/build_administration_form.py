
from extract.model.application import Application
from extract.model.facility import Facility
from extract.model.operator import Operator


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
    "comments" : "CIIP 2018 import",
    "facility": facility_data,
    "operator": operator_data,
    "applicationMetadata": app_metadata
  }

  return form