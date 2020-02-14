import pymongo
import nltk
from nltk.stem import WordNetLemmatizer
#nltk.download('wordnet')
client = pymongo.MongoClient("mongodb+srv://admin:admincs121@cluster0-zsift.mongodb.net/test?retryWrites=true&w=majority") #connects to mongodb
db = client['test-database'] #creates db
col = db['test-collection'] #creates Collection

invInd = col.find_one()
lemmatizer = WordNetLemmatizer()
def retrieve_token(query: str) -> []:
	""" This function will take in a query of what the user wants to search for
		lemmatize it, search it in the database of the inverted index and return the result"""
	query = lemmatizer.lemmatize(query)

	return invInd[query]

def retrieve_urls(postings: [dict]) -> []:
	""" Takes in a list of postings which are in dict format and will take that doc_ID retrieve 
		each URLS in order and return it in a list"""
		##TODO: retrieve the actual URLS, retrievable from the bookkeeping json file
	#print(doc_ID)
	result = []
	for p in postings:
		result.append(p["doc_id"])
	return result

def print_information(urls: list) -> None:
	"""prints out the list of urls"""
	## TODO: make it look fancier
	for i in urls:
		print(i)
	return

def search_engine() -> None:
	"""asks the user to input a query and displays the list of urls that contains the word"""
	print("Welcome to our search engine")
	print("Please input any word to begin searching")
	print("To exit, enter: IW2ENP")

	query = input("Search for: ")
	while query != "IW2ENP":
		postings = retrieve_token(query)
		urls = retrieve_urls(postings)
		print_information(urls)
		query = input("Search for: ")

	return

if __name__ == "__main__":
	#print(invInd)
	#x = retrieve_token("nice")
	#print(x)
	#print(retrieve_urls(x))
	print(lemmatizer.lemmatize("informatics"))
	search_engine()


