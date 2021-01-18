import itertools
import json
import util
from util import get_sheet_value, zero_if_not_number

ciip_swim_gas_types = {
    'Carbon dioxide from non-biomass (CO2)': 'CO2nonbio',
    'Carbon dioxide from biomass not listed in Schedule C of GGERR (CO2)': 'CO2bioNC',
    'Carbon dioxide from biomass listed in Schedule C of GGERR  (bioCO2) ': 'CO2bioC',
    'Methane (CH4)': 'CH4',
    'Nitrous oxide (N2O)': 'N2O',
    'Sulfur Hexafluoride (SF6)': 'SF6',
    'Perfluoromethane (CF4)': 'CF4',
    'Perfluoroethane (C2F6)':'C2F6',
}

ciip_swim_emissions_categories = {
    'Stationary Fuel Combustion Emissions ': 'General Stationary Combustion',
    'Venting Emissions': 'Venting',
    'Flaring Emissions':'Flaring',
    'Fugitive/Other Emissions': 'Fugitive',
    'On-Site Transportation Emissions': 'On-Site Transportation',
    'Waste and Wastewater Emissions': 'Waste and Wastewater',
    'Industrial Process Emissions': 'Industrial Process'
}

def extract(ciip_book):
    emissions_sheet = ciip_book.sheet_by_name('Emissions')
    emissions = []

    current_emission_cat = None
    for row in range(2, emissions_sheet.nrows - 1, 2) : # ignore the last row
        if get_sheet_value(emissions_sheet, row, 5) is None: # it's the category header
            current_emission_cat = ciip_swim_emissions_categories.get(get_sheet_value(emissions_sheet, row, 1))
            if current_emission_cat is None: # we went too far, there's probably some junk at the bottom of the sheet
                break
        else :
            quantity = zero_if_not_number(get_sheet_value(emissions_sheet, row, 4))
            gas_description = get_sheet_value(emissions_sheet, row, 1)
            emissions.append(
                {
                    "sourceTypeName" : current_emission_cat,
                    "gasType" : ciip_swim_gas_types.get(gas_description),
                    "gasDescription" : gas_description,
                    "annualEmission" : quantity,
                    "annualC02e" : zero_if_not_number(get_sheet_value(emissions_sheet, row, 8))
                }
            )

    non_zero_emissions = filter(lambda e : e['annualEmission'] != 0 or e['annualC02e'] != 0, emissions)

    return {sourceType:list(gases) for sourceType,gases in itertools.groupby(non_zero_emissions, lambda emission : emission['sourceTypeName'])}