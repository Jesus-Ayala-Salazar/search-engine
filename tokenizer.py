import sys
import os
from bs4 import BeautifulSoup
import nltk
from collections import defaultdict
import pymongo
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import math
from model.Posting import Posting
from nltk.corpus import wordnet
import datetime
import json


# IDF(t) = log_e(Total number of documents / Number of documents with term t in it).

# create database connection
client = pymongo.MongoClient("mongodb+srv://admin:admincs121@cluster0-zsift.mongodb.net/test?retryWrites=true&w=majority") #connects to mongodb

# initialize appropriate collections from MongoDB
db = client["engine-database"]
collecTest = db["InvertedIndex_update"]
lengthCollec = db["LengthCollec_update"]


def map_pos_tag(tag: str) -> str:
    """
    maps from nltk pos tag schema to wordnet lemmatizer schema
    nltk uses treebank pos tags found here: https://www.clips.uantwerpen.be/pages/MBSP-tags
    modified from: https://stackoverflow.com/questions/15586721/wordnet-lemmatization-and-pos-tagging-in-python
    """
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('R'):
        return wordnet.ADV
    else:   # treat rest of tags as nouns
        return wordnet.NOUN


def calculate_weight(tf_idf: float, freq_dict:{str:int}) -> float:
    """
    calculates and returns weighted term frequency of a token in a document
    html tag classes and weights:
    plain: 1, strong: 8, h3-h6: 1, h1-h2: 6, anchor: 8, title: 4
    based on: https://www.usenix.org/legacy/publications/library/proceedings/usits97/full_papers/cutler/cutler.pdf
    """
    WEIGHT_FACTOR = {"plain": 0,'strong': 4, 'h3-h6': 1, 'h1-h2': 3, 'a': 4, 'title': 2}
    weight = tf_idf
    for tag in freq_dict:
        for freq in range(freq_dict[tag]):
            weight += WEIGHT_FACTOR[tag]
    return weight


def calculate_tf(freq_dict: {str: int}) -> int:
    """
    calculates total freq of each document
    """
    result = 0
    for tag in freq_dict:
        result += freq_dict[tag]
    return result #TF


def encode_posting(postings: set) -> [tuple]:
    """
    takes in a set of postings associated with a unique token.
    returns a sorted list of 2-tuples: (doc_id, tfidf) for the given token.
    sorting by tfidf before creating the index allows for faster times
      during retrieval phase.
    """
    result = []
    for p in postings:
        result.append((p.doc_id,p.tf_idf))
    result.sort(key=(lambda tup: tup[1]), reverse=True)
    return result


def tokenize_file(dirname, doc_id, lemmatizer, length_dict) -> {str: Posting}:
    """
    Creates and returns a dictionary mapping each token in the given doc_id html 
    file to its corresponding Posting to be added later to the inverted index.
    """
    # create absolute path to each html file
    html_filename = os.path.join(dirname, doc_id)

    # create soup object to parse for text
    with open(html_filename, 'rb') as html_file:
        soup = BeautifulSoup(html_file, 'lxml')
        # get title
        title = soup.find('title')
        if not title:
            title = ''
        else:
            title = title.get_text()[:100]

        # get first paragraph
        first_p = soup.find('p')
        if not first_p:
            first_p = ''
        else:
            first_p = first_p.get_text()[:280]

    # {token: single Posting}
    single_posting_dict = defaultdict(lambda: Posting(doc_id))

    # for string in document
    for s in soup.strings:
        # for token in string
        text = nltk.word_tokenize(s)
        for t, tag in nltk.pos_tag(text):
            # lemmatize
            token = lemmatizer.lemmatize(t.lower(), map_pos_tag(tag))
            # filtering
            if token.isascii() and len(token) > 1 and token not in set(stopwords.words('english')):
                increment_tags(token, s.parent.name, single_posting_dict)

    # check if single_posting_dict has valid tokens
    #  if yes, add it to length_dict
    if single_posting_dict:
        length_dict[doc_id].append(title)
        length_dict[doc_id].append(first_p)
    return single_posting_dict


def increment_tags(token: str, tag: str, single_posting_dict: {str: Posting}):
    """
    Increments the token frequency of the token in the current 
      html file based on the token's html tag. Used later for
      calculating tfidf based on importance of html tags.
    """
    if tag in {'h1', 'h2'}:
        single_posting_dict[token].tags['h1-h2'] += 1
    elif tag in {'h3', 'h4', 'h5', 'h6'}:
        single_posting_dict[token].tags['h3-h6'] += 1
    elif tag == 'title':
        single_posting_dict[token].tags['title'] += 1
    elif tag == 'a':
        single_posting_dict[token].tags['a'] += 1
    elif tag == 'strong':
        single_posting_dict[token].tags['strong'] += 1
    else:
        single_posting_dict[token].tags['plain'] += 1


def create_postings_dict(data: {str: str}, filename: str, postings_dict: {str: {Posting}}, length_dict: {str: (float, str, str)}):
    """
    creates an inverted index consisting of tokens mapped to a set of its
      Postings
    returns the number of documents with valid tokens
    """
    # get web pages directory, create lemmatizer
    dirname = os.path.dirname(filename)
    lemmatizer = WordNetLemmatizer()
    num_documents = 0
    
    # iterate over each html file
    for doc_id in data:
        single_posting_dict = tokenize_file(dirname, doc_id, lemmatizer, length_dict)

        # add each Posting from current document to global dictionary
        for token in single_posting_dict:
            postings_dict[token].add(single_posting_dict[token])

        # increment number of documents count
        # used for idf calculation
        if single_posting_dict:
            num_documents += 1

    return num_documents

            
def createLocationDictionary(filename: str) -> dict:
    '''
    Reads the bookkeeping.json file and returns a dictionary corresponding to a folder/file
    and what it's url is.
        key 	== folder/file (Str)
        value	== url (Str)
    '''
    with open(filename, 'r', encoding='utf8') as json_file:
        data = json.load(json_file)
    return data


if __name__ == "__main__":
    # get absolute path to url index file bookkeeping.json
    path = sys.argv[1]

    # inverted index mapping each unique token to its set of postings
    # {token: set of Postings}
    postings_dict = defaultdict(set)


    # extract html identifiers from json file
    data = createLocationDictionary(path)  # {"folder/file" : "URL"}

    # {doc_id: [H1, first-paragraph, length]}
    # this dictionary maps document ids to an array of its h1 text,
    #   first <p> tag text, and its document vector length
    # used for database insertion
    length_dict = defaultdict(list)

    # begin timing tokenization
    begin_time_of_tokenizing = datetime.datetime.now()
    print("run tokenizing")

    # keeps track of total documents with valid tokens
    # used for calculating idf of each token
    num_documents = create_postings_dict(data, path, postings_dict, length_dict)

    # end timing tokenization
    print("finish tokenizing")
    end_time_of_tokenizing = datetime.datetime.now()
    print("Time of commencement (TOKENIZING):", begin_time_of_tokenizing)
    print("Time finish(TOKENIZING): ", end_time_of_tokenizing)


    # {token: idf}
    # maps unique tokens to their idf in the corpus and is used for database insertion
    idf_dict = {}

    for token in postings_dict:
        # calculate idf
        idf = math.log(num_documents / len(postings_dict[token]), 10)
        idf_dict[token] = idf

        for posting in postings_dict[token]:
            # calculate tf-idfs of each token for each posting
            tf = 1 + math.log(calculate_tf(posting.tags), 10)
            posting.tf_idf = tf*idf
            posting.tf_idf = calculate_weight(posting.tf_idf,posting.tags)
            # check that vector length hasn't been initialized
            if len(length_dict[posting.doc_id]) == 2:
                length_dict[posting.doc_id].append(0.0)
            # calculate squares of each vector component in the equation:
            #   ||doc_id|| = sqrt(x1^2 + x2^2 + ... + xn^2)
            #   used later to calculate each document's vector magnitude
            length_dict[posting.doc_id][2] += posting.tf_idf ** 2


    # calculate the square root and insert into a data structure for DB insertion
    insert_length_dict =[] #data structure for DB insertion
    for doc_id in length_dict:
        # get html file H1 and
        length_dict[doc_id][2] = math.sqrt(length_dict[doc_id][2])
        insert_length_dict.append({"doc_id": doc_id, "length": length_dict[doc_id][2], 'title': length_dict[doc_id][0], 'first-p': length_dict[doc_id][1], 'url': data[doc_id]})
    lengthCollec.insert_many(insert_length_dict)    # insert to MongoDB

    # print sorting times for debugging
    count = 0
    print("begin sorting, appending to dict, and inserting into DB")
    begin_time = datetime.datetime.now()

    # sort by tf-idf
    # after it is sorted encode each posting associated with that token
    # then make a dictionary that will pass it into the MongoDB
    insert_dict = []    # needed for MongoDB insertion
    for t in postings_dict:
        insert_dict.append({"token":t, "postings": encode_posting(postings_dict[t]), 'idf': idf_dict[t]})
        if count % 50000 == 0:
            print(f"count: {count}")
        count += 1

    collecTest.insert_many(insert_dict)    # insert to MongoDB

    # print sorting times for debugging
    end_time = datetime.datetime.now()
    print("END sorting, appending to dict, and inserting into DB")
    print("Time of commencement (INSERTION):", begin_time)
    print("Time finish(INSERTION): ", end_time)
