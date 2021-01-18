import psycopg2
import psycopg2.extras
import util
from util import get_sheet_value, reduce_dicts_array, partial_dict_eq, search_row_index

## returns True if two contact dicts represent the same individual
def should_merge_contacts(a,b):
    return partial_dict_eq(a, b, ['first_name', 'last_name', 'position', 'email', 'phone'])


def addresses_eq(a, b):
    return partial_dict_eq(a, b, ['street_address', 'municipality', 'province', 'postal_code'])

def extract(ciip_book):
    admin_sheet = ciip_book.sheet_by_name('Administrative Info')
    cert_sheet = ciip_book.sheet_by_name('Statement of Certification')
    co_header_idx = search_row_index(cert_sheet, 1, 'Signature of Certifying Official')

    rep_addr =  {
        'streetAddress'  : get_sheet_value(admin_sheet, 24, 1),
        'municipality'    : get_sheet_value(admin_sheet, 24, 3),
        'province'        : get_sheet_value(admin_sheet, 26, 1),
        'postalCode'     : get_sheet_value(admin_sheet, 26, 3)
    }

    co_addr =  {
        'streetAddress'  : get_sheet_value(cert_sheet, co_header_idx + 11, 1),
        'municipality'    : get_sheet_value(cert_sheet, co_header_idx + 11, 4),
        'province'        : get_sheet_value(cert_sheet, co_header_idx + 13, 1),
        'postalCode'     : get_sheet_value(cert_sheet, co_header_idx + 13, 4)
    }

    contacts = {
        "certifying_official_contact":{
            'firstName'      : get_sheet_value(cert_sheet, co_header_idx + 7, 1),
            'lastName'       : get_sheet_value(cert_sheet, co_header_idx + 7, 4),
            'position'        : get_sheet_value(cert_sheet, co_header_idx + 9, 1),
            'email'           : get_sheet_value(cert_sheet, co_header_idx + 9, 4),
            'phone'           : get_sheet_value(cert_sheet, co_header_idx + 9, 6),
            'address'         : co_addr
        },
        "operational_representative_contact":{
            'firstName'      : admin_sheet.cell_value(18, 1),
            'lastName'       : admin_sheet.cell_value(18, 3),
            'position'        : admin_sheet.cell_value(20, 1),
            'email'           : admin_sheet.cell_value(20, 3),
            'phone'           : admin_sheet.cell_value(22, 1),
            'address'         : rep_addr
        }
    }
    
    return contacts