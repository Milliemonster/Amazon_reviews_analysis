import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def word_count(input_txt, want_words = False):
    '''
    INPUT: string, bool
    OUTPUT: int, list if bool True

    Analyzes a string and counts the words. Return word count and optional list
    of the words in the text if want_words is True

    '''

    my_words = [] #complete list of words in document
    new_word = ''

    input_text = str(input_txt)
    for i in range (len(input_text)):
        input_text.replace('.' , '')
        input_text.replace("'" , '')

        if input_text[i].isalpha() == True:
            new_word += input_text[i]
        elif (input_text[i] in {' ', '.', '?', ',', ';', ':'} and new_word != ''):
            my_words.append(new_word)
            new_word = ''
    if (new_word != ''):
        my_words.append(new_word)

    if want_words:
        return (len(my_words), my_words)
    else:
        return (len(my_words))

def unique_words(input_text):
    '''
    INPUT: string
    OUTPUT: set

    Returns a list of unique words in the input string.

    '''
    my_words, number = word_count(input_text)
    unique_words = set(my_words) #set of unique words
    return unique_words


if __name__ == '__main__':
    #read in csv and create dataframe sorted by most helpful review
    rev_df = pd.read_csv('data/top_review_set.csv')

    #Adds a column with a word count for the body of each review
    rev_df['review_word_count'] = 0
    words = []
    for i in range(len(rev_df)):
        length = word_count(rev_df.loc[i, 'review_body'], False)
        rev_df.loc[i, 'review_word_count'] = length

    #Select columns and write to csv
    for_regression = rev_df.loc[:, ['product_id', 'star_rating','helpful_votes',
    'total_votes', 'vine', 'verified_purchase', 'review_date', 'review_word_count']]
    for_regression.to_csv('data/for_regression.csv', index = False)
