import numpy as np
import pandas as pd
import re
import os.path
import pycrfsuite as crf
from itertools import chain
from evaluate import getfeatures
from parse import preprocess, tokenize, isquantity, isunit, standardize, asfloat, tokenmatch

"""
Parse a CSV where the row is formatted like NYT cooking dataset:

input:str,                   name:str, qty:float, range_end:float, unit:str,  comment:str
"2 tbsp of garlic, chopped", "garlic", 2.0,       0.0,             "tbsp",    "chopped"

Train a linear chain CRF using python-crfsuite and output a model file
"""

def matchtags(row):
    """
    Match each token (lowercase) in the input (raw text) to the appropriate label, if it exists
    - We attempt to match singular and pluralized tokens ("shallot", "shallots")
    - Matching of fractions and floats are handled (1 1/2, 1.50) - rounding to 2 decimal places
    - We attemps to match units in alternative representations (tbsp, T, tablespoon)
    """
    
    tokens = tokenize(preprocess(row["input"]))
    ingr_tokens = tokenize(preprocess(row["name"]).lower())
    comment_tokens = tokenize(preprocess(row["comment"]).lower())
    unit_tokens = tokenize(preprocess(row["unit"]).lower())
    
    labels = []
    
    for token in tokens:
        
        if asfloat(token) == row["qty"]: 
            labels.append("QTY")
        
        elif asfloat(token) == row["range_end"]:
            labels.append("QTY-UR")
        
        elif any(tokenmatch(standardize(token).lower(), u) for u in unit_tokens):
            labels.append("UNIT")
        
        elif any(tokenmatch(token.lower(), i) for i in ingr_tokens):
            labels.append("INGR")
        
        elif token.lower() in comment_tokens:
            labels.append("CMNT")
        
        else:
            labels.append(None)
    
    return [tokens, labels]

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

def generatedata(path: str, testprop = 0):
    """
    Return parsed and formatted sequences X,y to pass to python-crfsuite
    X is a list of dictionaries containing features for each word
    y is a list of labels with IOB tags
    
    If testprop is specified, split X,y into training and testing sets
    Return X_train, y_train, X_test, y_test (in that order)
    """
    
    df = pd.read_csv(path)
    
    # Filter entries whose original entry (input) or ingredient name are missing
    df = df.loc[pd.notna(df.name)&pd.notna(df.input)]
    
    matched = df.apply(matchtags, axis=1)
    
    if testprop > 0 and testprop < 1:
        
        test = matched.sample(frac=testprop)
        train = matched.drop(test.index)
        
        X_train = list(chain.from_iterable(train.apply(lambda line: getfeatures(line[0]))))
        y_train = list(chain.from_iterable(train.apply(lambda line: iobtag(line[1]))))
        X_test = list(chain.from_iterable(test.apply(lambda line: getfeatures(line[0]))))
        y_test = list(chain.from_iterable(test.apply(lambda line: iobtag(line[1]))))
        
        return X_train, y_train, X_test, y_test
        
    else:
        
        X = list(chain.from_iterable(matched.apply(lambda line: getfeatures(line[0]))))
        y = list(chain.from_iterable(matched.apply(lambda line: iobtag(line[1]))))

        return X, y

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
    
    model = crf.Trainer()
    model.verbose = verbose
    model.append(X, y)
    
    # Modify the parameters if specified
    if params is not None: model.set_params(params)
    
    model.train(output)
    print("Model successfully trained and saved as: " + output)
    return output