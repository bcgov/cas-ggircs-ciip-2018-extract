from model.facility import Facility
import util
from util import get_sheet_value, none_if_not_number

def extract(ciip_book, cursor, operator):
    facility = Facility(operator)

    admin_sheet = ciip_book.sheet_by_name('Administrative Info')

    bcghg_id = str(get_sheet_value(admin_sheet, 8, 3)).replace('.0', '').strip() if get_sheet_value(admin_sheet, 8, 3) is not None else None

    facility.name = get_sheet_value(admin_sheet, 30, 1, operator.trade_name)
    facility.bcghg_id = str(bcghg_id)
    facility.type = get_sheet_value(admin_sheet, 32, 1)
    facility.naics = int(get_sheet_value(admin_sheet, 32, 3, get_sheet_value(admin_sheet, 10, 3, 0)))
    facility.description = get_sheet_value(admin_sheet, 42, 1) if admin_sheet.nrows >= 43 else None

    cursor.execute(
        '''
        select distinct swrs_facility_id from swrs.identifier
        where identifier_value = %s
        ''',
        (facility.bcghg_id,)
    )

    res = cursor.fetchone()
    if res is not None:
        facility.swrs_facility_id = res[0]
    else: # try using  the facility name
        cursor.execute(
            '''
            select distinct swrs_facility_id from swrs.facility
            where lower(facility_name) = %s
            ''',
            (facility.name,)
        )
        res = cursor.fetchall()
        if res is not None and len(res) == 1:
            facility.swrs_facility_id = res[0][0]

    # Outlier: This partial facility name match is the only way to match this row in the ciip_2018 data to a swrs_id in the swrs data.
    if 'oda cre' in facility['name'].lower():
        facility['swrs_facility_id'] = 14235

    if 'Production' in ciip_book.sheet_names():
        production_sheet = ciip_book.sheet_by_name('Production')
        facility.production_calculation_explanation = get_sheet_value(production_sheet, 47, 2)
        facility.production_additional_info = get_sheet_value(production_sheet, 51, 2)
        facility.production_public_info = get_sheet_value(production_sheet, 55, 2)

    return facility
