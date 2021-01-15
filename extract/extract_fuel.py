import util
from util import get_sheet_value

def extract(ciip_book):
  fuel_sheet = ciip_book.sheet_by_name('Fuel Usage') if 'Fuel Usage' in ciip_book.sheet_names() else ciip_book.sheet_by_name('Fuel Usage ')
  fuels = []
  use_alt_fuel_format = get_sheet_value(fuel_sheet, 3, 0) != 'Fuel Type '
  row_range = range(4, fuel_sheet.nrows) if not use_alt_fuel_format else range(5, fuel_sheet.nrows - 1, 2)

  for row in row_range:
    fuel = {}
    if use_alt_fuel_format:
      fuel = {
        'fuel_type' : get_sheet_value(fuel_sheet, row, 1),
        'fuel_type_alt' : get_sheet_value(fuel_sheet, row, 3),
        'fuel_description' : get_sheet_value(fuel_sheet, row, 5),
        'quantity' : get_sheet_value(fuel_sheet, row, 7),
        'fuel_units' : get_sheet_value(fuel_sheet, row, 9),
        'carbon_emissions' : get_sheet_value(fuel_sheet, row, 11),
      }
    else:
      fuel = {
        'fuel_type' : get_sheet_value(fuel_sheet, row, 0),
        'fuel_type_alt' : None,
        'fuel_description' : get_sheet_value(fuel_sheet, row, 1),
        'quantity' : get_sheet_value(fuel_sheet, row, 2),
        'fuel_units' : get_sheet_value(fuel_sheet, row, 3),
        'carbon_emissions' :  get_sheet_value(fuel_sheet, row, 4),
      }

    if not (fuel['fuel_type'] is None and fuel['fuel_type_alt'] is None and fuel['fuel_description'] is None): # skip rows without any label
      try:
        if fuel['quantity'] is not None:
          fuel['quantity'] = float(fuel['quantity'])
        if fuel['carbon_emissions'] is not None:
            fuel['carbon_emissions'] = float(fuel['carbon_emissions'])
        fuels.append(fuel)
      except:
          print('Could not parse Fuel row: ' + ','.join(str(e) for e in fuel.values()))

    return fuels
