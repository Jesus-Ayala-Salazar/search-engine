import pymongo
import nltk
from nltk.stem import WordNetLemmatizer
import json
import sys
import math
import os
import pprint
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.corpus import wordnet
#nltk.download('wordnet')
client = pymongo.MongoClient("mongodb+srv://admin:admincs121@cluster0-zsift.mongodb.net/test?retryWrites=true&w=majority") #connects to mongodb
db = client['test-database'] #creates db
# col = db['invertedIndex'] #creates Collection
col = db['firstTestIndex']
lengthCol = db['lengthCollec']

#col2 = db["test-collection"]
#test_coss = [{"token": "dog", "postings":{"d2": 1.2, "d3" : 1.23, "d1": 0.12}}, {"token": "cat", "postings": {"d1": 0, "d2": 0.2, "d3": 1.2}}]
#col2.insert_many(test_coss)
#### TESTING INSERTS
#token = {"token": "ics", "postings": [{"doc1": "10/10"}]}
#token_list = {"token": "informatics", "postings": [{"doc1": "10/10"}]}, {"token": "stat", "postings": [{"doc2": "11/11"}]}
#col.insert_one(token)
#col.insert_many(token_list)

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

lemmatizer = WordNetLemmatizer()
def retrieve_postings(dict_query: {str:float}) -> [dict]:
    """ This function will take in a query of what the user wants to search for
            search it in the database of the inverted index and return the result"""
    #list_query = query.split()
    cosine_scores = defaultdict(float)
    length_doc = defaultdict(float)
    for q in dict_query:
        dbDocument = col.find_one({"token":f"{q.lower()}"})
        tfidf_dict = dbDocument['postings']
        for doc_id in tfidf_dict:
            # calculates dot product
            cosine_scores[doc_id] += dict_query[q] * tfidf_dict[doc_id]
            length_doc[doc_id] = lengthCol.find_one({"doc_id":doc_id})["length"]
    # calculate query magnitude/length
    query_magnitude = 0
    for q in dict_query:
        query_magnitude += dict_query[q]**2
    query_magnitude = math.sqrt(query_magnitude)

    # perform equation
    for document_id in cosine_scores:
        cosine_scores[document_id] = cosine_scores[document_id]/(query_magnitude*length_doc[document_id])

    # sort by cosine score increasing
    # list of doc_ids sorted by increasing cosine score
    for k in sorted(cosine_scores, key=lambda x: cosine_scores[x], reverse=True):
        print(f'{k} : {cosine_scores[k]}')
    return sorted(cosine_scores, key=lambda x: cosine_scores[x], reverse=True)


def calc_query_tfidf(query:str):
    return None

def posting_tfidf(p:dict):
    """ Used to sort the postings by td_idf"""
    return p["tf_idf"]
def retrieve_urls(postings: [dict], locationDictionary: dict) -> []:
    """ Takes in a list of postings which are in dict format and will take that doc_ID retrieve
        each URLS in order and return it in a list"""
        ##TODO: retrieve the actual URLS, retrievable from the bookkeeping json file
    #print(doc_ID)

    urlResultList = []
    #print(postings)
    for doc_id in postings:
        urlResultList.append(locationDictionary[doc_id])
    # for posting in postings:
    # 	folderLocation = posting["doc_id"]
    # 	urlResultList.append(locationDictionary[folderLocation])
    return urlResultList

def print_information(urls: list) -> None:
    """prints out the list of urls"""
    print("\n_______________________URL RESULTS_______________________")
    count = 0
    for url in urls:
        if count <20:
            print(url)
        count +=1
    print("_________________________________________________________\n")

    return

def search_engine(locationDictionary: dict) -> None:
    """asks the user to input a query and displays the list of urls that contains the word"""
    print("Welcome to our search engine")
    print("Please input any word to begin searching")
    print("To exit, enter: !q")


    while True:
        query = input("Search for: ")
        if query == "!q":
            break
        ### LEMMATIZE EACH WORD IN QUERY
        query = nltk.word_tokenize(query)
        token_freq = defaultdict(int)
        for t, tag in nltk.pos_tag(query):
            # filtering
            if t.isascii() and len(t) > 1 and t not in set(stopwords.words('english')):
                # add lemmatized token to list, increment frequency
                token = lemmatizer.lemmatize(t.lower(), map_pos_tag(tag))
                token_freq[token] += 1

        query_tfidf = defaultdict(float) #dict of each token to its tfidf
        for token in token_freq:
            db_doc = col.find_one({"token": token})
            print(f'token: {token} ')
            query_tfidf[token] = token_freq[token]*db_doc["idf"]

        postings = retrieve_postings(query_tfidf)
        if postings == []:
            continue
        urls = retrieve_urls(postings, locationDictionary)
        print_information(urls)

    return

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

def queryExists(query:str) -> bool:
    '''
    Takes in a query and checks to see if query exists in db
        returns a bool
    '''
    count = col.find({f"{query}": {"$exists": True}})
    if count > 0:
        return True
    return False

if __name__ == "__main__":
    # test = col.find_one({"token":"stat"})
        # print(test['postings'])

    path = sys.argv[1]
    urlLocationDictionary = createLocationDictionary(path)
    search_engine(urlLocationDictionary)


