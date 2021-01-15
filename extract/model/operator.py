
from .application import Application

class Operator:
  id = 0
  application = None

  legal_name = None
  trade_name = None
  duns = None
  bc_corp_reg = None
  is_bc_cop_reg_valid = False
  orgbook_legal_name = None
  is_registration_active = None
  swrs_operator_id = None

  def __init__(self, application):
    self.application = application
    return


  def save(self, cursor):
    cursor.execute(
      (
        'insert into ciip_2018_load.operator '
        '(application_id, business_legal_name, english_trade_name, bc_corp_reg_number, '
        'is_bc_corp_reg_number_valid, orgbook_legal_name, is_registration_active, duns, swrs_operator_id) '
        'values (%s, %s, %s, %s, %s, %s, %s, %s, %s) '
        'returning id'
      ),
      (
        self.application.id, 
        self.legal_name,
        self.trade_name,
        self.bc_corp_reg,
        self.is_bc_cop_reg_valid,
        self.orgbook_legal_name,
        self.is_registration_active,
        self.duns,
        self.swrs_operator_id
      )
    )
    self.id = cursor.fetchone()[0]
    return self.id