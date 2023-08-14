import re

from nltk.stem import PorterStemmer
import nltk
nltk.download('punkt')

from nltk.tokenize import word_tokenize

stopwords_english = []
sentences_clean = []

def __init__():
    with open('src/Stopword-List.txt', 'r') as f:
            stopWord = f.readline()
            while stopWord:
                stopwords_english.append(stopWord.strip())
                stopWord = f.readline()


def process_sentence(sentence, docid, typ='', idx=0):
    """Process sentence function.
    Input:
        sentence: a string containing a sentence
    Output:
        sentences_clean: a list of words containing the processed sentence
    """
    global sentences_clean
    if typ == 'q':
        sentences_clean = []
    stemmer = PorterStemmer()
    # removing special characters
    sentence = re.sub(r'\W+', ' ', sentence)
    # tokenize sentence
    word_tokens = word_tokenize(sentence.lower())

    for word in word_tokens:
        if (word not in stopwords_english):  # remove punctuation
            # tweets_clean.append(word)
            stem_word = stemmer.stem(word)  # stemming word
            # stem_word = word
            if typ == 'q':
                sentences_clean.append(stem_word)
            else:
                sentences_clean.append((stem_word, docid, idx))
                idx = idx + 1
        else:
            idx = idx + 1

    return idx


def getSentences():
    return sentences_clean
