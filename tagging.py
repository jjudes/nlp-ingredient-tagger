import re
import pycrfsuite as crf
from training import getfeatures

def getlabels(ingredients, model_path):
    
    tagger = crf.Tagger()
    tagger.open(model_path)
    
    if type(ingredients) is str: 
        return tagger.tag(getfeatures(ingredients))
    else:
        return [tagger.tag(getfeatures(item)) for item in ingredients]
        
def removeiob(labels):
    
    if type(labels) is str: labels = [labels]
    
    removed = []
    
    for label in labels:
        
        if label=='O':
            removed.append("")
        elif label[0:2]=='B-' or label[0:2]=='I-':
            removed.append(label[2:])
        else:
            remove.append(label)
    
    return removed

def rejoin(tokens):
    """
    Roughly invert the tokenize function for preprocessed string
    """
    
    string = [] # Parse tokens and join with spaces
    punctuation = {'.', ',', ':', ';', '!', ']', ')'}
    
    for i in range(len(tokens)):
        
        # Add spaces and prettify fractional quantities
        if re.match(r'(\d+\$)(\d+)/(\d+)$', tokens[i]):
            frac = tokens[i].split('$')
            string.append(frac[0])
            if frac[1] in unicode:
                string.append(unicode[frac[1]])
            else:
                string.append(frac[1])
        
        # Make sure spaces aren't added between text and punctuation
        elif tokens[i] in punctuation and len(string)>0:
            string[-1] = string[-1]+tokens[i]
        
        else:
            string.append(tokens[i])
        
        #Handle opening parentheses
        if len(string)>1 and string[-2] in {'(', '['}:
            string[-2] = string[-2] + string[-1]
            string.pop()
    
    return ' '.join(string)
