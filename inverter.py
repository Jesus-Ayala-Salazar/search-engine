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
#### TESTING INSERTS
#token = {"token": "ics", "postings": [{"doc1": "10/10"}]}
#token_list = {"token": "informatics", "postings": [{"doc1": "10/10"}]}, {"token": "stat", "postings": [{"doc2": "11/11"}]}
#col.insert_one(token)
#col.insert_many(token_list)


lemmatizer = WordNetLemmatizer()
def retrieve_postings(query: str) -> []:
	""" This function will take in a query of what the user wants to search for
			lemmatize it, search it in the database of the inverted index and return the result"""
	dbDocument = col.find_one({"token":f"{query}"})
	#print(f"postings for {query}:", dbDocument)
	if dbDocument == None:
		return []
	postingsList = dbDocument['postings']
	return postingsList

def retrieve_urls(postings: [dict], locationDictionary: dict) -> []:
	""" Takes in a list of postings which are in dict format and will take that doc_ID retrieve 
		each URLS in order and return it in a list"""
		##TODO: retrieve the actual URLS, retrievable from the bookkeeping json file
	#print(doc_ID)
	
	urlResultList = []
	for posting in postings:
		folderLocation = posting["doc_id"]
		urlResultList.append(locationDictionary[folderLocation])
		

	return urlResultList

def print_information(urls: list) -> None:
	"""prints out the list of urls"""
	print("\n_______________________URL RESULTS_______________________")
	for url in urls:
		print(url)
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
		query = lemmatizer.lemmatize(query)
		# print("you entered:", query)
		# if not queryExists(query):
		# 	print(".")
		# 	continue
		#print("query after lemmitzation:", query)
		postings = retrieve_postings(query)
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


