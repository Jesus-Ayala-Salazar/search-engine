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
#nltk.download('wordnet') ##this downloads just once to put it in your PC

### CONNECTS TO CLIENT MONGODB
client = pymongo.MongoClient("mongodb+srv://admin:admincs121@cluster0-zsift.mongodb.net/test?retryWrites=true&w=majority") #connects to mongodb
db = client['engine-database'] #Connects to the database where our inverted index is located
col = db['test-01']
lengthCol = db['test-length-01'] #Connects to a collection that contains the document_ID along with its length and URL
lemmatizer = WordNetLemmatizer() #Used to lemmatize the query in order to match the process in the tokenizer


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


def cos_similarity(dict_query: {str:float}) -> [dict]:
    """ Takes in a dictionary of query where the Key: Term in query and 
    	Value:td_idf of the query it performs cosSimilarity and returns scores sorted"""

    cosine_scores = defaultdict(float) ##a dictionary where the key is doc_id and value is its score
    length_doc = defaultdict(float) ### dictionary of the coressponding doc that have the query.
    for q in dict_query:
        tfidf_list = col.find_one({"token":f"{q}"})['postings'][:100] #retrieve the document of the query/term
                                                                     #retrieve its postings in form {doc_id:td-idf}
        for doc_id,tf_idf in tfidf_list: 
            # calculates dot product
            cosine_scores[doc_id] += dict_query[q] * tf_idf #build cosine_scores by dot product
            length_doc[doc_id] = lengthCol.find_one({"doc_id":doc_id})["length"] # get the length of each doc_id that we come across
    # calculate query magnitude/length
    query_magnitude = 0 ##calculate length of query ||query||
    for q in dict_query:
        query_magnitude += dict_query[q]**2
    query_magnitude = math.sqrt(query_magnitude)

    # perform equation
    # the final value of cosine scores is calculated
    for document_id in cosine_scores:
        cosine_scores[document_id] = cosine_scores[document_id]/(query_magnitude*length_doc[document_id]) ##Q.DOC/||Q||*||D||

    # sort by cosine score increasing
    # list of doc_ids sorted by decreasing cosine score

    ## TESTING; DELETE FOR FINAL TURN IN
    # for k in sorted(cosine_scores, key=lambda x: cosine_scores[x], reverse=True):
    #      print(f'{k} : {cosine_scores[k]}')
    return sorted(cosine_scores, key=lambda x: cosine_scores[x], reverse=True)


def retrieve_urls(document_ids: [str]) -> []:

    """ Takes in a list of document IDS that are already sorted and will take that doc_ID retrieve
        each URLS in order from the Database and return it in a list"""
    #build a list of urls
    urlResultList = []

    count = 0
    for doc_id in document_ids:
        if count <20:
            doc_db = lengthCol.find_one({"doc_id":doc_id})
            url_info = (doc_db["title"],doc_db["url"],doc_db["first-p"])
            urlResultList.append(url_info)
            count+=1
    
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

def calculate_querytdf_idf(query:[str]) -> {}:
    """ takes in a list of terms and returns a dict with its weight associated"""
    token_freq = defaultdict(int) ## Used to calculate the weight of each term in query
    for t, tag in nltk.pos_tag(query):
        # filtering
        if t.isascii() and len(t) > 1 and t not in set(stopwords.words('english')):
            # add lemmatized token to list, increment frequency
            token = lemmatizer.lemmatize(t.lower(), map_pos_tag(tag))
            token_freq[token] += 1

    query_tfidf = defaultdict(float) #dict of each token to its tfidf
    for token in token_freq:
        if queryExists(token):
            db_doc = col.find_one({"token": token}) #Retrieve the token and its idf to calc its tf_idf
            ##DELETE BUT KEEP FOR NOW FOR TESTING
            ##print(f'token: {token} ')
            # calcualte td_idf of query
            query_tfidf[token] = token_freq[token]*db_doc["idf"]
    return query_tfidf

#For Non-GUI querying
def search_engine() -> None:

    """asks the user to input a query and displays the list of urls that contains the word"""
    print("Welcome to our search engine")
    print("Please input any word to begin searching")
    print("To exit, enter: !q")


    while True:
        query = input("Search for: ")
        if query == "!q":
            break
        ### LEMMATIZE EACH TERM IN QUERY
        #use same format when creating the indexer to get same results
        query = nltk.word_tokenize(query)
        
        query_tfidf = calculate_querytdf_idf(query)

        #RETRIEVE THE DOC_IDS IN ORDER by using cos sim
        postings = cos_similarity(query_tfidf)
        if postings == []:
            continue
        urls = retrieve_urls(postings)
        print_information(urls)

    return

## USED FOR GUI!
def obtainRelevantPages(query) -> list:
    query = nltk.word_tokenize(query)    
    query_tfidf = calculate_querytdf_idf(query)

    #RETRIEVE THE DOC_IDS IN ORDER by using cos sim
    postings = cos_similarity(query_tfidf)
    urls = retrieve_urls(postings)
    
    return urls

 
def queryExists(query:str) -> bool:
    '''
    Takes in a query and checks to see if query exists in db
        returns a bool
    '''
    db_doc = col.count_documents({"token":query}) #if >0 then it is true
    if db_doc > 0:
        return True
    return False

if __name__ == "__main__":

    #path = sys.argv[1]
    search_engine()


