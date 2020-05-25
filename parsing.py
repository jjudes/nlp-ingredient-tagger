import re
from pandas import isna

# Limited set of stopwords in recipes for parsing
stopwords = {'a', 'an', 'at', 'any', 'as', 'about', 
             'by', 'but' 'for', 'in', 
             'is', 'it', 'its', 'or', 'of', 'to'}

# Symbol set for parsing
symbols = {',', '.', '(', ')', ':', ';', '/',
          '"', "'", '!', '@', '#', '$', '%', 
           '&', '-', '+', '?'}

# Plaintext representation of unicode fraction
unicode = {
    '½':'1/2','⅓':'1/3','⅔':'2/3',
    '¼':'1/4','¾':'3/4',
    '⅕':'1/5','⅖':'2/5','⅗':'3/5','⅘':'4/5',
    '⅙':'1/6','⅚':'5/6','⅐':'1/7',
    '⅛':'1/8','⅜':'3/8','⅝':'5/8','⅞':'7/8',
    '⅑':'1/9','⅒':'1/10',
    '¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9',
    '₁':'1','₂':'2','₃':'3','₄':'4','₅':'5','₆':'6','₇':'7','₈':'8','₉':'9'
}

# Unicode vulgar fractions
fractions = {
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

def asciifractions(string):
    """
    Convert unicode fractions to plaintext
    """
    
    parsed = []
    for i in range(len(string)):
        if string[i] in unicode:
            # Ensure "1½" maps to "1 1/2", not "11/2"
            if i>0 and string[i-1].isdigit(): parsed.append(' ')
            parsed.append(unicode[string[i]])
        elif string[i]=='⁄':
            parsed.append('/')
        else:
            parsed.append(string[i])
    return ''.join(parsed)

def clumpfractions(string):
    
    """
    Standardize fractions of the form "A b/c" as "A$b/c"
    Handle fractions in unicode format
    """

    return re.sub(r'(\d+)\s+(\d)/(\d)', r'\1$\2/\3', string)

def clean(string):
    """
    Remove HTML tags, unclump digits, add/remove spaces as necessary
    """
    
    #Remove HTML tags
    return re.sub('<.*?>', '', string)
    #Split digit,unit clumps (2tbsp -> 2 tbsp)
    string = re.sub(r'(\d+)([a-zA-Z])', r'\1 \2', string)
    # Insert spaces at '/' when non-numeric (500 grams/2 cups -> 500 grams / 2 cups)
    string = re.sub(r'([^0-9\s])/', r'\1 / ', string)
    
    return re.sub('\s+', ' ', string)

# def tokenize(string):
#     """Split into list of tokens, treating punctuation as tokens"""
        
#     # Separate pad parentheses with spaces
#     string = re.sub(r'([\[\]\(\),!:;])', r' \1 ', string)
#     string = re.sub(r'([a-zA-Z])\.', r'\1 .', string)
    
#     # Remove superfluous spaces and split into list
#     return re.sub('\s+', ' ', string).strip().split(' ')

def tokenize(string, preprocess=False, getpositions = False):
    """
    Tokenize the string acording to the following rules:
    * Split on any whitespace
    * Split on [ ] ( ) , ! : ; and include as token
    * If not part of float or fraction, split on . / and include as token
    Return a list of tokens and a list of substring indices
    """
    
    if isna(string) or not string: 
        if getpositions: return [], []
        return []
    
    if preprocess:
        string = clumpfractions(asciifractions(clean(string)))
    
    prefixes = {'(', '[', '"', "'", '#'}
    suffixes = {')', ']', '"', "'", ':', ';', ',', '.', '?', '%'}
    
    matches = re.finditer(r'\S+', string)
    
    tokens = []
    positions = []
    
    for match in matches:
        token = match.group(0)
        start = match.start()
        end = match.end()
        
        #Strip prefixes
        while token and token[0] in prefixes:
            tokens.append(token[0])
            positions.append((start, start+1))
            token = token[1:]
            start += 1
            
        #Collect suffixes
        stokens = []
        while token and token[-1] in suffixes:
            stokens.append(token[-1])
            token = token[:-1]
            end -= 1
        
        if token:
            tokens.append(token)
            positions.append((start, end))
        
        for suffix in reversed(stokens):
            tokens.append(suffix)
            positions.append((end, end+1))
            end += 1
        
    if getpositions: return tokens, positions
    return tokens

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
    """
    
    # Float or int in form 000 or 000.000
    match = re.match('([0-9]+)(\.[0-9]+)?$', token)
    if match: return float(match.group(0))
        
    # Fraction in form X$x/x
    match = re.match(r'(\d+\$)?(\d+)/(\d+)$', token)
    if match:
        whole = 0 if not match.group(1) else int(match.group(1)[:-1]) #drop $
        frac = int(match.group(2))/int(match.group(3))
        return whole+frac
    
    return -1.0

def round_2f(x):
    """
    Round positive numbers to two decimal places, 0.5 always rounds up
    (Python does not round this way by default)
    """
    if x==-1: 
        return -1
    else:
        return int(100*x + 0.5)/100
    
def iobtag(labels):
    """
    Add IOB tags to the labels to improve prediction
    B-XXXX Beginning of XXXX label
    I-XXXX Inside (not beginning) of XXXX label
    O No label assigned
    """
    
    iob = []
    
    for i in range(len(labels)):

        if labels[i] is None:
            iob.append("O")
        elif i == 0 or labels[i]!=labels[i-1]:
            iob.append("B-"+labels[i])
        else:
            iob.append("I-"+labels[i])

    return iob

def removeiob(labels):
    
    if type(labels) is str: labels = [labels]
    
    removed = []
    
    for label in labels:
        
        if label=='O':
            removed.append("")
        elif label[0:2]=='B-' or label[0:2]=='I-':
            removed.append(label[2:])
        else:
            removed.append(label)
    
    return removed
