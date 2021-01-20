import psycopg2
import util
from util import get_sheet_value, none_if_not_number

def extract(ciip_book):
    elec_sheet = None
    row_range = None
    col_range = None
    if 'Electricity' in ciip_book.sheet_names():
        elec_sheet = ciip_book.sheet_by_name('Electricity')
        row_range = range(4, 7, 2)
        col_range = range(1, 10, 2)
    else:
        elec_sheet = ciip_book.sheet_by_name('Electricity and Heat')
        row_range = range(5, 7)
        col_range = range(1, 6)


    elec_and_heat = filter(
        lambda product: not (product['quantity'] is None and product['associatedEmissions'] is None),
        [
            {
                "productName" : "Purchased Electricity",
                "quantity" : none_if_not_number(get_sheet_value(elec_sheet, row_range[0], col_range[0])),
                "units" : "MWh",
                "associatedEmissions" : None
            },
            {
                "productName" : "Generated Electricity",
                "quantity" : none_if_not_number(get_sheet_value(elec_sheet, row_range[0], col_range[1])),
                "units" : "MWh",
                "associatedEmissions" : none_if_not_number(get_sheet_value(elec_sheet, row_range[0], col_range[4]))
            },
            {
                "productName" : "Consumed Electricity",
                "quantity" : none_if_not_number(get_sheet_value(elec_sheet, row_range[0], col_range[2])),
                "units" : "MWh",
                "associatedEmissions" : None
            },
            {
                "productName" : "Sold Electricity",
                "quantity" : none_if_not_number(get_sheet_value(elec_sheet, row_range[0], col_range[3])),
                "units" : "MWh",
                "associatedEmissions" : None
            },
            {
                "productName" : "Purchased Heat",
                "quantity" : none_if_not_number(get_sheet_value(elec_sheet, row_range[1], col_range[0])),
                "units" : "GJ",
                "associatedEmissions" : None
            },
            {
                "productName" : "Generated Heat",
                "quantity" : none_if_not_number(get_sheet_value(elec_sheet, row_range[1], col_range[1])),
                "units" : "GJ",
                "associatedEmissions" : none_if_not_number(get_sheet_value(elec_sheet, row_range[1], col_range[4]))
            },
            {
                "productName" : "Consumed Heat",
                "quantity" : none_if_not_number(get_sheet_value(elec_sheet, row_range[1], col_range[2])),
                "units" : "GJ",
                "associatedEmissions" : None
            },
            {
                "productName" : "Sold Heat",
                "quantity" : none_if_not_number(get_sheet_value(elec_sheet, row_range[1], col_range[3])),
                "units" : "GJ",
                "associatedEmissions" : None
            }
        ]
    )

    return list(elec_and_heat)
