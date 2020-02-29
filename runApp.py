from flask import Flask, render_template, request, redirect, url_for
import sys
sys.path.append('../')
import querying
app = Flask(__name__)

@app.route('/results', methods = ['GET', 'POST'])
def results():
    query = request.args.get("query")
    print("get request of query: ", query)
  
    if query == '': #is empty
        return redirect('/')
  
    #res=somelookupfunction(query) #lst should now be tuples of (h1, link, sometext)
    listOfResults = retrieveURLs(query)

    # res = buildResultList(listOfURLS)
    return render_template("results.html", inputtedQuery = query, list_of_results = listOfResults)

@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')

def retrieveURLs(query: str) -> list:
    '''Function takes in a query and goes to the backend to obtain the relevant pages '''
    listOfURLS = querying.obtainRelevantPages(query)
    return listOfURLS

# def buildResultList(listOfURLS: list):
#     '''function creates the required data structure necessary (of the results) for the template rendering'''
#     result = []
#     for URL in listOfURLS:
#         result.append(("Header", URL, "Lorem ipsum dolor sit amet, ea eum nisl magna, qui mazim laudem ei. Commodo aperiam abhorreant id vimLorem ipsum dolor sit amet, ea eum nisl magna, qui mazim laudem ei. Commodo aperiam abhorreant id vimLorem ipsum dolor sit amet, ea eum nisl magna, qui mazim laudem ei. Commodo aperiam abhorreant id vim"))
#     return result

if __name__ == '__main__':
    app.run(debug = True)