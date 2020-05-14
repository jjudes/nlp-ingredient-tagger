import re
from pandas import isna
import unicodedata as uc

# Some relevant stopwords in recipes for parsing
stopwords = {'a', 'an', 'at', 'any', 'as', 'about', 
             'by', 'but' 'for', 'in', 
             'is', 'it', 'its', 'or', 'of', 'to'}

# Symbol set for parsing
symbols = {',', '.', '(', ')', ':', ';', '/',
          '"', "'", '!', '@', '#', '$', '%', 
           '&', '-', '+', '?'}

# Plaintext representation of unicode fraction
fractions = {
    '½':'1/2','⅓':'1/3','⅔':'2/3',
    '¼':'1/4','¾':'3/4',
    '⅕':'1/5','⅖':'2/5','⅗':'3/5','⅘':'4/5',
    '⅙':'1/6','⅚':'5/6','⅐':'1/7',
    '⅛':'1/8','⅜':'3/8','⅝':'5/8','⅞':'7/8',
    '⅑':'1/9','⅒':'1/10',
    '¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9',
    '⁄':'/',
    '₁':'1','₂':'2','₃':'3','₄':'4','₅':'5','₆':'6','₇':'7','₈':'8','₉':'9'
}

# Unicode vulgar fractions
unicode = {
    '1/2':'½','1/3':'⅓','2/3':'⅔',
    '1/4':'¼','3/4':'¾',
    '1/5':'⅕','2/5':'⅖','3/5':'⅗','4/5':'⅘',
    '1/6':'⅙','5/6':'⅚','1/7':'⅐',
    '1/8':'⅛','3/8':'⅜','5/8':'⅝','7/8':'⅞',
    '1/9':'⅑','1/10':'⅒'
}

# Common singular representation of units/abbreviations
units = {
    'T':'tablespoon',
    'T.':'tablespoon',
    'tbsp':'tablespoon',
    'tbsp.':'tablespoon',
    'Tbsp':'tablespoon',
    'Tbsp.':'tablespoon',
    'tablespoon':'tablespoon',
    'tablespoons':'tablespoon',

    't':'teaspoon',
    't.':'teaspoon',
    'tsp':'teaspoon',
    'tsp.':'teaspoon',
    'teaspoon':'teaspoon',
    'teaspoons':'teaspoon',
    
    'cup':'cup',
    'c':'cup',
    'C':'cup',
    'c.':'cup',
    'C.':'cup',
    'cup':'cup',
    'cups':'cup',
    'Cup':'cup',
    'Cups':'cup',
    
    'fl':'fluid',
    'fluid':'fluid',
    'fl oz':'fluid ounce',
    'fl.oz.':'fluid ounce',
    'fl.oz': 'fluid ounce',
    'fluid ounce':'fluid ounce',

    'qt':'quart',
    'qt.':'quart',
    'quart':'quart',
    'quarts':'quart',

    'gal':'gallon',
    'gallon':'gallon',
    'gallons':'gallon',

    'ml':'milliliter',
    'mL':'milliliter',
    'milliliter':'milliliter',
    'milliliters':'milliliter',
    'millilitre':'milliliter',
    'millilitres':'milliliter',

    'l':'liter',
    'L':'liter',
    'liter':'liter',
    'liters':'liter',
    'litre':'liter',
    'litres':'liter',

    'g':'gram',
    'g.':'gram',
    'gram':'gram',
    'grams':'gram',

    'mg':'milligram',
    'milligram':'milligram',
    'milligrams':'milligram',

    'k':'kilogram',
    'kg':'kilogram',
    'kilogram':'kilogram',
    'kilograms':'kilogram',

    'oz':'ounce',
    'oz.':'ounce',
    'ounce':'ounce',
    'ounces':'ounce',

    'lb':'pound',
    'lbs':'pound',
    'lb.':'pound',
    'lbs.':'pound',
    'pound':'pound',
    'pounds':'pound',

    'in':'inch',
    'in.':'inch',
    'inch':'inch',
    'inches':'inch',

    'cm':'centimeter',
    'centimeter':'centimeter',
    'centimeters':'centimeter',

    'clove':'clove',
    'slice':'slice',
    'piece':'piece',
    'fillet':'fillet',
    'sprig':'sprig',
    'stick':'stick',
    'leave':'leaf',
    'package':'package',
    'can':'can',
    'bottle':'bottle',
    'handful':'handful',
    'dash':'dash',
    'pinch':'pinch',
    
    'cloves':'clove',
    'slices':'slice',
    'pieces':'piece',
    'fillets':'fillet',
    'sprigs':'sprig',
    'sticks':'stick',
    'leaves':'leaf',
    'packages':'package',
    'cans':'can',
    'bottles':'bottle',
    'handfuls':'handful',
    'dashes':'dash',
    'pinches':'pinch'
}

def remove_html(string):
    """Remove HTML tags and contents"""
    return re.sub('<[^<]+?>', '', string)

def parse_fractions(string):
    
    """
    Standardize fractions of the form "A b/c" as "A$b/c"
    Handle fractions in unicode format
    """
    
    # Convert unicode fractions to plaintext
    parsed = []
    for i in range(len(string)):
        if string[i] in fractions:
            if i>0 and string[i-1].isdigit(): parsed.append(' ')
            parsed.append(fractions[string[i]])
        else:
            parsed.append(string[i])
    string = ''.join(parsed)
    
    # Unitize multi-term fractions with $ (e.g. 1 1/2 -> 1$1/2)
    string = re.sub(r'(\d+)\s+(\d)/(\d)', r'\1$\2/\3', string)
    
    return string.lstrip()

def clean(string):
    """Add spaces where necessary and remove superfluous spaces"""
    
    #Split quantity,unit clumps (2tbsp -> 2 tbsp)
    string = re.sub(r'(\d+)([a-zA-Z])', r'\1 \2', string)
    # Insert space at '/' when non-numeric
    string = re.sub(r'([^0-9\s])/', r'\1 / ', string)
    
    return re.sub('\s+', ' ', string)

def preprocess(line):
    """Pipe through pre-processing functions defined above"""
    
    if type(line) is not str or line is "": return ""
    
    pipe = [remove_html, parse_fractions, clean]
    for f in pipe:
        line = f(line)
    return line

def tokenize(string):
    """Split into list of tokens, treating punctuation as tokens"""
        
    # Separate pad parentheses with spaces
    string = re.sub(r'([\[\]\(\),!:;])', r' \1 ', string)
    string = re.sub(r'([a-zA-Z])\.', r'\1 .', string)
    
    # Remove superfluous spaces and split into list
    return re.sub('\s+', ' ', string).strip().split(' ')

def tokenmatch(x, y):
    """
    Naively check if x and y are the same token up to pluralization
    """
    
    if not x or not y: return False # Handle empty strings and None/NaN values
    if (x==y): return True
    
    if x not in stopwords and x not in symbols:
        if y[-1]=='s' and x in y: return True
    if y not in stopwords and y not in symbols:
        if x[-1]=='s' and y in x: return True
    
    return False

def isunit(token):
    """Check if token represents a unit"""
    return token in units

def standardize(unit):
    
    """
    Convert unit abbreviations into standard singular form
    e.g. Tbsp., T, tablespoons -> tablespoon
    """
    
    # If not passed string, assume iterable of strings
    if type(unit) is not str:
        return [standardize(u) for u in unit]
    else:
        return units.get(unit, unit)

def isquantity(token):
    """
    Check if token is numeric, formated as "000" "000.000" or "0$0/0"
    """
    if re.match('[0-9]+\.?[0-9]*$', token) or re.match(r'(\d+\$)?(\d+)/(\d+)$', token):
        return True
    return False

def asfloat(token):
    """
    Convert tokens "000.000" or "00$00/00" into float to two decimal places
    Negative and non-float tokens return -1.0
    Rounding is modified so that 0.005 is always rounded up e.g. 1/8 -> 0.13
    """
    
    round_ = lambda x: int(100*float(x)+0.5)/100
    
    # Float or int in form 000 or 000.000
    match = re.match('([0-9]+)(\.[0-9]+)?$', token)
    if match: return round_(match.group(0))
        
    # Fraction in form X$x/x
    match = re.match(r'(\d+\$)?(\d+)/(\d+)$', token)
    if match:
        whole = 0 if not match.group(1) else int(match.group(1)[:-1]) #drop $
        frac = int(match.group(2))/int(match.group(3))
        return round_(whole+frac)
    
    return -1.0