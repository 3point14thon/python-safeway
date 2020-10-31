

def homogenize_unit(unit):
    '''
    converts input str to unit compatable with unitconvert python library

    Args:
        unit(str): unit to be converted

    Returns:
        string representing input unit in format compatable with unitconvert
    '''
    unit = unit.lower()
    aliases = {'milli': 'm',
               'gram': 'g',
               'ounce': 'oz',
               'pound': 'lb',
               'kilo': 'k',
               'teaspoon': 'tsp',
               'tablespoon': 'tbsp',
               'fluid': 'fl',
               'pint': 'pt',
               'quart': 'qt',
               'gallon': 'gal',
               'liter': 'l'}
    for alias in aliases:
        if alias in unit:
            unit = unit.replace(alias, aliases[alias])
    ok_chars = '3abcfgiklmnopqstuz'
    unit = [char for char in unit if char in ok_chars]
    return ''.join(unit).rstrip('s')


import safeway


file_dir = safeway.__file__.replace('__init__.py', 'user_data.txt')
with open(file_dir, 'a'):
    pass
