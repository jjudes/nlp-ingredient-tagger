import pycrfsuite as crf
from training import getfeatures
from parsing import removeiob

def getlabels(ingredients:str, model_path):
    """
    Accepts a string and returns tags for each token
    Tokenizer is as specified in parsing.py
    """
    
    tagger = crf.Tagger()
    tagger.open(model_path)
    
    return tagger.tag(getfeatures(ingredients))
    
def evaluate(X, y, model_path):
    """
    Compute accuracy, precision, recall, and F-score per entity and across all entities
    X: List of dictionaries representing features each the token
    y: True labels for each token
    model_path: The path to the output of python-crfsuite model
    Output dictionaries: accuracy, precision, recall, fscore
        Keys of dictionary are each label in y (entities) and 'Total' (all entities)
        Values of dictionary are the corresponding metric for the key
    """
    
    tagger = crf.Tagger()
    tagger.open(model_path)
        
    true = removeiob(y)
    pred = removeiob(tagger.tag(X))
    
    # Counting entities, predictions and matches
    npred = {}
    ntrue = {}
    correct = {}
        
    for i in range(len(true)):
        
        ntrue[true[i]] = ntrue.get(true[i], 0) + 1
        npred[pred[i]] = npred.get(pred[i], 0) + 1
        
        if true[i]==pred[i]:
            correct[true[i]] = correct.get(true[i], 0) + 1
    
    # Compute each metric per entity
    accuracy = {}
    precision = {}
    recall = {}
    fscore = {}
    
    entities = ['INGR', 'QTY', 'QTY-UR', 'UNIT']
    
    for e in entities:
        
        cor_entities = correct.get(e, 0)
        cor_nonentities = correct.get('', 0)
        n_entities = ntrue.get(e, 0)
        n_nonentities = ntrue.get('', 0)
        n_predicted = npred.get(e, 0)
        
        if n_entities+n_nonentities > 0:
            accuracy[e] = (cor_entities + cor_nonentities)/(n_entities + n_nonentities)
        else:
            accuracy[e] = None
        
        if n_predicted > 0:
            precision[e] = cor_entities/n_predicted
        else:
            precision[e] = 0
        
        if n_entities > 0:
            recall[e] = cor_entities/n_entities
        else:
            recall = 0
        
        if precision[e]+recall[e] > 0:
            fscore[e] = 2*(precision[e]*recall[e])/(precision[e]+recall[e])
        else:
            fscore[e] = 0
    
    # Compute overall accuracy
    accuracy['Total'] = sum(correct.values())/sum(ntrue.values())
    
    # Remove non-entity counts (equivalently setting to 0) and compute precision/recall
    correct['']=0
    npred['']=0
    ntrue['']=0
    
    if sum(npred.values()) > 0:
        precision['Total'] = sum(correct.values())/sum(npred.values())
    else:
        precision['Total'] = 0
        
    if sum(ntrue.values()) > 0:
        recall['Total'] = sum(correct.values())/sum(ntrue.values())
    else:
        recall['Total'] = 0
        
    if precision['Total']+recall['Total'] > 0:
        fscore['Total'] = 2*(precision['Total']*recall['Total'])/(precision['Total']+recall['Total'])
    else:
        fscore['Total'] = 0
    
    return accuracy, precision, recall, fscore
