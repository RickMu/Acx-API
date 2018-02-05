'''
term frequency * inverse document frequency

n/doc_len *   log( Docs_number/(1+occurence_in_all_docs))


assuming the format is

{
        ETH:[
            p1,
            p2,
            p3,

        ]

        BTC : [
            p1,
            p2,
            p3
        ]

}


Intuition is:

    terms that appear across all docs of coins is good.
    but also that appeared only in one doc is also important

Assumption:
    Assuming all docs are writing about something similar in topic,
    therefore their choice of words will not vary too largely

Estimated Performance:
    Unsure

    Reasons:
        - too many English words, each doc may use very distinct words
            that doesn't mean much in terms of their tech

'''

import math
from alt_coin.text_filters import regex_clean

'''
Can check wikipedia to explore these function, choices
search tf_idf
'''

# should provide stopWords e.g 'a', 'the', etc, otherwise weighting will be greatly affected
def function_term_frequency(term_count, doc_length):
    #term count divide doc length
    #weighting = term_count/doc_length

    #log normalization --> words that appear too many times in a doc should be weighted similar to words that appear little
    weighting = (1+math.log(term_count,10))/doc_length

    return weighting


def function_inverse_doc_frequency(term_appearance, docs_count):

    #weighting = math.log(docs_count/term_appearance,10)

    #log smoothing, so no negative y at postive x
    weighting = math.log(1+(docs_count / term_appearance), 10)

    return weighting


def tf_idf(docs, min_=0, max_=1, stopWords = None):
    #doc_frequency is a dict for all docs
    doc_frequency = {}

    #term_frequecy will contain a dict for each doc
    term_frequency ={}

    docs_count = len(docs.keys())

    for doc in docs:
        doc_length = 0
        term_frequency[doc] = {}

        for para in docs[doc]:
            #string needs split by space
            para = regex_clean.remove_special_char(para)
            words = para.split(' ')

            doc_length+=len(words)

            for term in words:
                # do not want to include stopWords
                if stopWords is not None and term in stopWords:
                    continue
                if len(term)<= 4:
                    continue

                if term not in term_frequency[doc]:
                    term_frequency[doc][term]=1
                else:
                    term_frequency[doc][term] += 1


        #calculating term divide by doc length
        for term in list(term_frequency[doc].keys()):
            term_freq = function_term_frequency(term_frequency[doc][term],doc_length )

            if term_freq< min_ or term_freq>max_:
                del  term_frequency[doc][term]
            else:
                term_frequency[doc][term] = term_freq


    #counting the occurences of terms in all docs
    #appearance of a term in a doc not matter how many times is counted as 1
    for doc in term_frequency:
        for term in term_frequency[doc]:
            if term not in doc_frequency:
                doc_frequency[term]=1
            else:
                doc_frequency[term] += 1

    for term in doc_frequency:

        doc_frequency[term] = function_inverse_doc_frequency(doc_frequency[term], docs_count)

    return term_frequency, doc_frequency

def rating(term_frequency, doc_frequency):
    #Give a rating to each coin using the above formula
    alt_coins = {}
    docs_count = len(term_frequency.keys())

    for coin in term_frequency:
        alt_coins[coin]=0
        for term in term_frequency[coin]:
            term_tf_idf = term_frequency[coin][term]* doc_frequency[term]

            alt_coins[coin] +=term_tf_idf

    return alt_coins



def keywords_selection(docs, keywords):
    '''
    Purely to print out how many keywords are in each doc
    one keyword is only counted once
    '''

    keyword_dict = {}

    for doc in docs:
        keyword_dict[doc] ={}

        for para in docs[doc]:
            words = para.split(' ')

            for word in words:
                if word in keywords:
                    keyword_dict[doc][word] = 1

    keyword_counts = {}

    for doc in keyword_dict:
        keyword_counts[doc] = len(keyword_dict[doc].keys())

    return keyword_counts




if __name__ == "__main__":

    import json

    test1 ={

        'ETH': [
            'eth_distinct_word',
            'common_word',
        ],

        'BTC': [
            'btc_distinc_word',
            'common_word',
            'common_word',
            'common_word',
        ]
    }

    tf, df = tf_idf(test1)
    print(tf)
    print(df)
    coin_rating = rating(tf,df)
    print(coin_rating)

    keywords = ['common_word','eth_distinct_word']
    selection = keywords_selection(test1,keywords)

    print(selection)

    alt = json.loads(open('../altcoin').read())
    for key in alt:
        alt[key] = [str(s) for s in alt[key]]



    tf, df = tf_idf(alt)
    print(len(df))
    print(df)
    print(tf)

    coin_rating = rating(tf,df)
    print(coin_rating)
