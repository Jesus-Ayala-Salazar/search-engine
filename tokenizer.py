import os
from bs4 import BeautifulSoup
import lxml
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
				#print(str(folde
				with open(parent+"\\"+ folder+"\\" +file, "rb") as f:
					html= f.read()
					#html = "<HTML>test<p>test2</p></HTML>"
					soup = BeautifulSoup(html, "lxml")

					#print(folder, file)
					#break
				
		#break
	#print(str(soup.prettify()))
"""tokenize
INVIND[token] """
if __name__ == "__main__":
	print(client.list_database_names())
	pass 
	#tokenize_each_file("C:\\Users\\eduar\\121\\Assign3\\WEBPAGES_CLEAN")


