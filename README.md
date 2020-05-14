# Ingredient Tagger #

Note: The dataset is taken from https://github.com/nytimes/ingredient-phrase-tagger, and pre-processing is carried out in a similar fashion. Training in the NY Times implementation uses CRF++. The CRF implementation used here will be python-CRFsuite (also originally in C++), and will use a different feature-set.

### Problem ###

While recipe text aims to have a common and structured format, variations and preferences make rule-based parsing (say, with regex) convoluted and cumbersome. For instance, consider the following very similar phrases:

* 500 mL red wine, preferably Merlot
* 0.5L red wine, Merlot
* 2 cups dry red wine (Merlot works well)
* A bottle of dry red wine (you won't need all of it)
* 1 750mL bottle of Merlot, or any other dry red wine

While the content is roughly the same, variations in how the ingredient phrase can be written make brute-forced parsing difficult.

### Using an NLP Solution ###

A more eloquent and generalizable solution is collecting a dataset of labelled ingredients phrases with name, quantities, units, etc. and using natural language processing to implicitly learn the structure and dependencies of ingredient phrases. The problem can be translated as a **sequence prediction** problem.

In normal classification we would have a word *W* (e.g. "peel") and some possible labels *C1, C2, ..., Ck* (e.g. Ingredient Name, Quantity, Unit, Comments), and our task is to predict which label best fits *W*. But the words *around* *W* might inform our guess for it's label (e.g. "Lemon peel for garnishing" `[peel:Ingredient]` vs. "Lemon, peel removed"`[peel:Comment]`). Hence what we're interested in is the whole sequence of words in a phrase.

The problem in phrase tagging is given a sequence of words *W1, W2, W3, ..., Wn* (e.g. `[2, cups, of, flour, sifted]`) and some possible labels for these words, what is the best *sequence* of labels *Y1, Y2, Y3, ..., Yn* (e.g. `[qty, unit, none, name, comment]`) (where each *Yi* is one of *C1, C2, ..., Ck*).
