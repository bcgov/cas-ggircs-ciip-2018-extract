import psycopg2
import requests
from model.operator import Operator
from model.application import Application
import util
from util import get_sheet_value, none_if_not_number

DUNS_EXCLUDE_VALUES = ['000000000', '111111111', '123456789', '0']

def normalize_name(raw):
  normalized_abbrev = {
    'ltd'   : 'limited',
    'inc'   : 'incorporated',
    'corp'  : 'corporation'
  }

  raw_name = str(raw)

  normalized_name = str(raw_name).lower().strip('.')
  for key, value in normalized_abbrev.items():
    normalized_name.replace(key, value)

  return normalized_name

def get_swrs_id_by_name(operator, cursor):
    cursor.execute(
        """
        select swrs_organisation_id, business_legal_name, english_trade_name from swrs.organisation
        """
    )
    res=cursor.fetchall()
    for row in res:
        if normalize_name(operator.legal_name) == normalize_name(row[1]) or normalize_name(operator.trade_name) == normalize_name(row[2]):
            operator.swrs_operator_id = row[0]

def extract(ciip_book, cursor):
    operator = Operator()

    admin_sheet = ciip_book.sheet_by_name('Administrative Info')

    duns = get_sheet_value(admin_sheet, 8, 1)
    if type(duns) is str:
        duns = duns.replace('-', '')
        duns = duns.replace(' ', '')
    elif duns is not None:
        duns = str(int(duns))
    if duns in DUNS_EXCLUDE_VALUES:
        duns = None

    bc_corp_reg = get_sheet_value(admin_sheet, 10, 1)
    if bc_corp_reg is not None:
        bc_corp_reg = str(bc_corp_reg).replace(" ", "").replace('.0', '')

    operator.legal_name = get_sheet_value(admin_sheet, 4, 1)
    operator.trade_name = get_sheet_value(admin_sheet, 6, 1)
    operator.duns = duns
    operator.bc_corp_reg = bc_corp_reg
    operator.is_bc_cop_reg_valid = False # overwritten below if true

    if bc_corp_reg is not None:
        orgbook_req = requests.get(
            'https://orgbook.gov.bc.ca/api/v2/topic/ident/registration/' + bc_corp_reg + '/formatted')
        if orgbook_req.status_code == 200 :
            orgbook_resp = orgbook_req.json()
            operator.is_bc_cop_reg_valid = True
            operator.orgbook_legal_name = orgbook_resp['names'][0]['text']
            operator.is_registration_active = not orgbook_resp['names'][0]['inactive']

    if duns is not None:
        cursor.execute(
            """
            select distinct swrs_organisation_id from swrs.organisation
            where duns = %s
            """,
            (duns,)
        )
        res = cursor.fetchone()
        if res is not None:
            operator.swrs_operator_id = res[0]
        else:
            get_swrs_id_by_name(operator, cursor)
    else:
        get_swrs_id_by_name(operator, cursor)

    return operator
