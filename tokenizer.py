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
from inverter import createLocationDictionary
from nltk.corpus import wordnet
from string import ascii_letters, digits


# IDF(t) = log_e(Total number of documents / Number of documents with term t in it).
#
client = pymongo.MongoClient("mongodb+srv://admin:admincs121@cluster0-zsift.mongodb.net/test?retryWrites=true&w=majority") #connects to mongodb

# ### this should be ran when everything works.
db = client["test-database"]
collec = db["invertedIndex"]


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


# MUST ENCODE POSTING TO BE ABLE TO INPUT IT INTO THE DATABASE"
def encode_Posting(post: Posting):
    return {"_type": "Posting", "doc_id": post.get_doc_id(), "freq": post.get_freq(), "tags": post.get_tags(), "tf_idf": post.get_tf_idf()}

def encode_each_Posting(postings: list):
	result = []
	for p in postings:
		result.append(encode_Posting(p))
	return result
# MUST DECODE FROM DOCUMENT
def decode_Posting(document):
    assert document["_type"] == "Posting"
    return Posting(document["doc_id"], document["freq"], document["tags"], document["tf_idf"])

def sort_tfID(post: Posting):
    return post.get_tf_idf()
#mydict = {"ics": {"doc_10": 10}}
#mydict1 = {"yes": Posting("0/10")}

#col.insert_one(mydict)
#ol.insert_one(mydict1)

def tokenize_each_file(filename: str,
                       postings_dict: {str: [Posting]},
                       num_tokens_dict: {str: int}):
    """Given a directory open each file within the given corpus and tokenize"""

    # extract html identifiers from json file
    data = createLocationDictionary(filename)

    # get web pages directory
    dirname = os.path.dirname(filename)

    lemmatizer = WordNetLemmatizer()

    # iterate over each html file
    for doc_id in data:
        html_filename = os.path.join(dirname, doc_id)     # use '13/16' for html with title and body

        # need to get frequency in doc, doc_id, tags the token appears in
        with open(html_filename, 'rb') as html_file:
            soup = BeautifulSoup(html_file, 'lxml')
            num_tokens = 0
            # {token: single Posting}
            inner_dict = defaultdict(lambda: Posting(doc_id))
            important_tags = {'title','h1','h2','h3','h4','h5','h6','strong'}

            # for string in document
            for s in soup.strings:
                # for token in string
                text = nltk.word_tokenize(s)
                for t, tag in nltk.pos_tag(text):
                    # filtering
                    if t.isascii() and len(t) > 1 and t not in set(stopwords.words('english')):
                        # add lemmatized token to list, increment frequency
                        token = lemmatizer.lemmatize(t.lower(), map_pos_tag(tag))
                        num_tokens += 1
                        inner_dict[token].freq += 1

                        # if token in important tags, add it
                        if s.parent.name in important_tags:
                            inner_dict[token].tags[s.parent.name] += 1

            # add each Posting from current document to global dictionary
            for token in inner_dict:
                postings_dict[token].append(inner_dict[token])

            # add total number of tokens to doc_id dictionary
            num_tokens_dict[doc_id] = num_tokens

            # progress file to see number of current documents indexed
            # with open('progress.txt', 'a', encoding='utf8') as file:
            #     file.write(f'doc id: {doc_id} | num words: {num_tokens}\n')


if __name__ == "__main__":
    # ###testing
    # p1 = Posting("0/8", 10, {"h1": 3, "title": 2}, 0.01)
    # p2 = Posting("1/8", 22, {"h1": 1, "title": 1}, 0.05)
    # p3 = Posting("2/8", 20, {"h1": 4, "title": 5}, 0.06)
    # mydict = {"ics": [encode_Posting(p1), encode_Posting(p2), encode_Posting(p3)], "informatics": [encode_Posting(p1), encode_Posting(p2), encode_Posting(p3)], "data": [encode_Posting(p1), encode_Posting(p2), encode_Posting(p3)]}
    # col.insert_one(mydict)
    # invi = col.find_one()
    # print(invi)
    # ##END OF TESTING

    path = sys.argv[1]

    # # {token: [] of Postings}
    postings_dict = defaultdict(list)

    # # {doc_id: number of terms in document}
    num_tokens_dict = {}

    tokenize_each_file(path, postings_dict, num_tokens_dict)

    # # encode postings into a dict to add to mongodb
    # this dict will be added to db
    # {token: [] of encoded_Postings()}
    encoded_posting = defaultdict(list) #TODO: Delete this line

    # calculate tf-idf
    # copies posting_dict and encodes
    # write to postings.txt
    # all in same pass

    # num_documents = len(num_tokens_dict)
    # with open('postings.txt', 'w', encoding='utf8') as file:
    #     for t in postings_dict:
    #         file.write(f'{t}:\n')
    #         for p in postings_dict[t]:
    #             tf = p.freq / num_tokens_dict[p.doc_id]
    #             idf = math.log(num_documents / len(postings_dict[t]), 10)
    #             p.tf_idf = tf*idf
    #             file.write(f'{str(p)}\n')
    #             encoded_posting[t].append(encode_Posting(p))
    #         file.write('\n')

    num_documents = len(num_tokens_dict)
    for t in postings_dict:
        for p in postings_dict[t]:
            tf = p.freq / num_tokens_dict[p.doc_id]
            idf = math.log(num_documents / len(postings_dict[t]), 10)
            p.tf_idf = tf*idf
            # encoded_posting[t].append(encode_Posting(p))

    # sort by tf-idf 
	# after it is sorted encode each posting associated with that token
	# then make a dictionary that will pass it into the MongoDB
    for t in postings_dict:
    	postings_dict[t].sort(key = sort_tfID, reverse = True)
        collec.insert_one({"token": t, "postings": encode_each_Posting(postings_dict[t])})
		#collec.insert_one({"token": t, "Posting": encode_each_Posting(postings_dict[t])})


