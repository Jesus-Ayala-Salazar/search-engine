import pymongo
import nltk
from nltk.stem import WordNetLemmatizer
import json
import sys
import os
import pprint
#nltk.download('wordnet')
client = pymongo.MongoClient("mongodb+srv://admin:admincs121@cluster0-zsift.mongodb.net/test?retryWrites=true&w=majority") #connects to mongodb
db = client['test-database'] #creates db
col = db['invertedIndex'] #creates Collection
#col2 = db["test-collection"]
#test_coss = [{"token": "dog", "postings":{"d2": 1.2, "d3" : 1.23, "d1": 0.12}}, {"token": "cat", "postings": {"d1": 0, "d2": 0.2, "d3": 1.2}}]
#col2.insert_many(test_coss)
#### TESTING INSERTS
#token = {"token": "ics", "postings": [{"doc1": "10/10"}]}
#token_list = {"token": "informatics", "postings": [{"doc1": "10/10"}]}, {"token": "stat", "postings": [{"doc2": "11/11"}]}
#col.insert_one(token)
#col.insert_many(token_list)


lemmatizer = WordNetLemmatizer()
def retrieve_postings(list_query: [str]) -> [dict]:
    """ This function will take in a query of what the user wants to search for
            search it in the database of the inverted index and return the result"""
    #list_query = query.split()
    dbDocuments = [] #[dict]
    for q in list_query:
        dbDocument = col.find_one({"token":f"{q.lower()}"})
        if dbDocument != None:
            dbDocuments.extend(dbDocument['postings']) ##we lose token in this case
    #print(f"postings for {query}:", dbDocument)
    #if dbDocument == None:
    #	return []
    #postingsList = dbDocument['postings']
    return dbDocuments

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
    postings.sort(key=posting_tfidf, reverse = True)
    for posting in postings:
        folderLocation = posting["doc_id"]
        urlResultList.append(locationDictionary[folderLocation])
    # for posting in postings:
    # 	folderLocation = posting["doc_id"]
    # 	urlResultList.append(locationDictionary[folderLocation])

    urlResultList = list(dict.fromkeys(urlResultList))
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
        queries  = nltk.word_tokenize(query) # split the query to get each word
        for i in range(len(queries)):
            queries[i] = lemmatizer.lemmatize(queries[i]) #for each word lemmatize and modify the list


        #query = lemmatizer.lemmatize(query)
        # print("you entered:", query)
        # if not queryExists(query):
        # 	print(".")
        # 	continue
        #print("query after lemmitzation:", query)

        #pass in the query as a list of queries
        #returns a list of dictionaries, each query is called by find_one
        postings = retrieve_postings(queries)
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


