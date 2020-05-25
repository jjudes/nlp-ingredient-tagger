import numpy as np
import pandas as pd
import re
import os.path
import pycrfsuite as crf
from itertools import chain
from parsing import symbols, tokenize, standardize, isquantity, isunit, asfloat, tokenmatch, round_2f, iobtag, removeiob

"""
Parse a CSV where the row is formatted like NYT cooking dataset:

input:str,                   name:str, qty:float, range_end:float, unit:str,  comment:str
"2 tbsp of garlic, chopped", "garlic", 2.0,       0.0,             "tbsp",    "chopped"

Train a linear chain CRF using python-crfsuite and output a model file
"""

def matchtags(row):
    """
    Match each token in the input (raw text) to the appropriate label, if one exists
    - We attempt to match singular and pluralized tokens ("shallot", "shallots")
    - Matching of fractions and floats are handled (1 1/2, 1.50)
    - We attemps to match units in alternative representations (tbsp, T, tablespoon)
    Return list of labels
    """
    
    ingr_tokens = tokenize(row["name"], preprocess=True)
    unit_tokens = tokenize(row["unit"], preprocess=True)
    #comment_tokens = tokenize(row["comment"], preprocess=True)
    
    labels = []
    
    for token in row["input"]:
        
        if asfloat(token) == row["qty"]: 
            labels.append("QTY")
        
        elif round_2f(asfloat(token)) == row["range_end"]:
            labels.append("QTY-UR")
        
        elif any(tokenmatch(standardize(token).lower(), u.lower()) for u in unit_tokens):
            labels.append("UNIT")
        
        elif any(tokenmatch(token.lower(), i.lower()) for i in ingr_tokens):
            labels.append("INGR")
        
#         elif token.lower() in comment_tokens:
#             labels.append("CMNT")
        
        else:
            labels.append(None)
    
    return labels

def getfeatures(line):
    
    if type(line) is str: line = tokenize(line, preprocess=True)
    
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
            'unit' : isunit(token),
            'numeric' : isquantity(token),
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
                '+1symbol' : nxt in symbols
            }

        token_features.update(prev_features)
        token_features.update(next_features)
        features.append(token_features)

        if not isparenthetical and token == ',': comma = not comma
        if token == '(': isparenthetical = True

    return features

def generatedata(path: str, testprop = 0, parallel=False):
    """
    Return parsed and formatted sequences X,y to pass to python-crfsuite
    X is a list of dictionaries containing features for each word
    y is a list of labels with IOB tags
    
    If testprop>0 is specified, split X,y into training and testing sets
    Return X_train, y_train, X_test, y_test (in that order)
    """
    
    df = pd.read_csv(path)
    # Filter entries whose original entry (input) or ingredient name are missing
    df = df.loc[pd.notna(df.name)&pd.notna(df.input)]
    
    if parallel:
        
        from pandarallel import pandarallel
        pandarallel.initialize(verbose=False)
        
        df.input = df.input.parallel_apply(lambda line: tokenize(line, preprocess=True))
        labels = df.parallel_apply(matchtags, axis=1)
        ind = np.random.choice([True, False], size=len(labels), p=[1-testprop, testprop])

        features = df.input.parallel_apply(getfeatures)
        ioblabels = labels.parallel_apply(iobtag)
        
    else:
        
        df.input = df.input.apply(lambda line: tokenize(line, preprocess=True))
        labels = df.apply(matchtags, axis=1)
        ind = np.random.choice([True, False], size=len(labels), p=[1-testprop, testprop])

        features = df.input.apply(getfeatures)
        ioblabels = labels.apply(iobtag)
    
    X_train = list(chain.from_iterable(features[ind]))
    y_train = list(chain.from_iterable(ioblabels[ind]))
    X_test = list(chain.from_iterable(features[np.invert(ind)]))
    y_test = list(chain.from_iterable(ioblabels[np.invert(ind)]))
    
    if testprop == 0: return X_train, y_train
    return X_train, y_train, X_test, y_test
        
def trainCRF(X, y, output=None, params=None, verbose=False):
    """
    Pass X, y to python-crfsuite Trainer and output a model file
    output: Output model filename (should end in .crfsuite)
    params: Dictionary of pycrfsuite parameters to pass to model
    verbose: Whether or not to display updates/status during training
    """
    
    # Name the output file model{i}.crfsuite if unspecified
    path = 'model%d.crfsuite'
    i = 1
    while output is None:
        if not os.path.exists(path%i):
            output = path%i
        i+=1
    
    #Training
    model = crf.Trainer()
    model.verbose = verbose
    model.append(X, y)
    
    # Modify the parameters if specified
    if params is not None: model.set_params(params)
    
    model.train(output)
    print("Model successfully trained and saved as: " + output)
    return output
