import numpy as np
import pandas as pd
import re
import pycrfsuite as crf
from parse import preprocess, tokenize, isquantity, isunit, standardize, asfloat

stopwords = {'a', 'an', 'at', 'any', 'as', 'about', 
             'by', 'but' 'for', 'in', 
             'is', 'it', 'its', 'or', 'of', 'to'}

symbols = {',', '.', '(', ')', ':', ';', '/',
          '"', "'", '!', '@', '#', '$', '%', 
           '&', '-', '+', '?'}

def getfeatures(line):
    
    if type(line) is str: line = tokenize(preprocess(line))
    
    features = []
    comma = False
    isparenthetical = False

    for i in range(len(line)):

        token = line[i]
        if token == ')': isparenthetical = False

        token_features = {
            'token' : token.lower(),
            'capitalized' : token.istitle(),
            'parenthetical' : isparenthetical,
            'numeric' : isquantity(token),
            'standardunit' : isunit(token),
            'symbol' : token in symbols,
            'followscomma' : comma
        }

        if (i==0):
            prev_features = {'start': True}
        else:
            prv = line[i-1]
            prev_features = {
                '-1token' : prv.lower(),
                '-1capitalized' : prv.istitle(),
                '-1numeric' : isquantity(prv),
                '-1standardunit' : isunit(prv),
                '-1symbol' : prv in symbols
            }

        if (i == len(line)-1):
            next_features = {'end': True}
        else:
            nxt = line[i+1]
            next_features = {
                '+1token' : nxt.lower(),
                '+1capitalized' : nxt.istitle(),
                '+1numeric' : isquantity(nxt),
                '+1standardunit' : isunit(nxt),
                '+1symbol' : nxt in symbols
            }

        token_features.update(prev_features)
        token_features.update(next_features)
        features.append(token_features)

        if not isparenthetical and token == ',': comma = not comma
        if token == '(': isparenthetical = True

    return features

def getlabels(ingredients, model='initial_test.crfsuite'):
    
    tagger = crf.Tagger()
    tagger.open(model)
    
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
