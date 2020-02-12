import sys
import os
import sys
from bs4 import BeautifulSoup
import lxml
from nltk import word_tokenize
import pymongo

client = pymongo.MongoClient("mongodb+srv://admin:admincs121@cluster0-zsift.mongodb.net/test?retryWrites=true&w=majority")
db = client.test
SEdb = client["SEdb"]
col = SEdb["InvInd"]
print(db.list_collection_names())

#tokenize --> use algorithms
#dbdicto
def tokenize_each_file(parent: str):
	"""Given a directory open each file within the given corpus and tokenize"""
	c = 0
	for folder in os.listdir(parent):
		if folder.endswith(".json") or folder.endswith(".tsv"):
			continue
		else:
			for file in os.listdir(parent+"\\"+folder):
				with open(parent+"\\"+ folder+"\\" +file, "rb") as f:
					html= f.read()
					html = "<html>hello <p>world</html>"
					soup = BeautifulSoup(html, "lxml")

					title = soup.title
					h1 = soup.h1
					h2 = soup.h2
					h3 = soup.h3
					h4 = soup.h4
					body = soup.body.string
					p = soup.p.string
					print(body, "\n\n", p)
				break
		break

"""tokenize
INVIND[token] """
if __name__ == "__main__":
	print(client.list_database_names())
	path = sys.argv[1]
	tokenize_each_file(path)
