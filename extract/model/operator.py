
class Operator:
  id = 0

  legal_name = None
  trade_name = None
  duns = None
  bc_corp_reg = None
  is_bc_cop_reg_valid = False
  orgbook_legal_name = None
  is_registration_active = None
  swrs_operator_id = None

  ciip_db_id = None

  # TODO: address of the operator?

  def save(self, cursor):
    cursor.execute(
      (
        'insert into ggircs_portal.operator '
        '(swrs_organisation_id, reporting_year, operator_name, operator_trade_name, duns) '
        'values (%s, %s, %s, %s, %s) '
        'returning id'
      ),
      (
        self.swrs_operator_id,
        2018,
        self.legal_name,
        self.trade_name,
        self.duns
      )
    )
    self.id = cursor.fetchone()[0]
    return self.id
