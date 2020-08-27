

def homogenize_unit(unit):
    unit = unit.lower()
    aliases = {'milli': 'm'
            ,'gram': 'g'
            ,'ounce': 'oz'
            ,'pound': 'lb'
            ,'kilo': 'k'
            ,'teaspoon': 'tsp'
            ,'tablespoon': 'tbsp'
            ,'fluid': 'fl'
            ,'pint': 'pt'
            ,'quart': 'qt'
            ,'gallon': 'gal'
            ,'liter': 'l'}
    for alias in aliases:
        if alias in unit:
            unit.replace(alias, aliases[alias])
    ok_chars = '3abcfgiklmnopqstuz'
    unit = [char for char in unit if char in ok_chars]
    return ''.join(unit).rstrip('s')
