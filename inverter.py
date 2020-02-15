import pymongo
import nltk
from nltk.stem import WordNetLemmatizer
import json
import sys
import os
#nltk.download('wordnet')
client = pymongo.MongoClient("mongodb+srv://admin:admincs121@cluster0-zsift.mongodb.net/test?retryWrites=true&w=majority") #connects to mongodb
db = client['test-database'] #creates db
col = db['invertedIndex'] #creates Collection

invInd = col.find()
lemmatizer = WordNetLemmatizer()
def retrieve_token(query: str) -> []:
	""" This function will take in a query of what the user wants to search for
		lemmatize it, search it in the database of the inverted index and return the result"""
	result = col.find({},{query:1})
	# query = lemmatizer.lemmatize(query)
	print("going to look for:", query)
	return result

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
		if not queryExists(query):
			print(".")
			continue
		postings = retrieve_token(query)
		urls = retrieve_urls(postings, locationDictionary)
		print_information(urls)
		query = input("Search for: ")

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
	
	#print(invInd)
	#x = retrieve_token("nice")
	#print(x)
	#print(retrieve_urls(x))
	#print(lemmatizer.lemmatize("informatics"))
	
	path = sys.argv[1]
	urlLocationDictionary = createLocationDictionary(path)
	test = col.find_one({"token":"stat"})
	print(test['postings'])
	#search_engine(urlLocationDictionary)


