# Information

## Undersample Training Set

All papers containing paragraphs titled with "problem description" or "problem statement", or having such words within the text were considered in the training set.
Subsections of each paper have been uploaded and these are considered as objects of the training set.

Each subsection is labeled as 'PD' if:
- belongs to a paragraph titled as "problem description" or "problem statement"
- contains in the text "problem description" or "problem statement"
- is "close" to a sub-section that contains "problem description" or "problem statement" in the text.

The other subsections have been labeled as 'N_PD'. There are situations in which it is not certain that some sub-sections are necessarily 'N_PD' and, having an unbalanced training set, it has been decided to eliminate them.

## Text Cleaning Training Set

All subsections in the training set have been processed: after an initial cleaning phase, the stopwords are removed and the remaining words are stemmed (or lemmatized).

## Classifiers

It is an attempt to evaluate the performance of various classifiers using cross-validation and combining different feature extraction methods. It takes a long time to run.

## Compute Classifiers

In this phase, several classifiers were computed.

## Test Set

Creation and prediction on test set           ->> sistema

## Data Set

Creation of data set: all the subsections belonging to a paragraph (with the exception of "References") have been considered and each of their text has been processed with a cleaning phase (identical to those applied in the training and test sets).

##
