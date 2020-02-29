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


if __name__ == '__main__':
    app.run(debug = True)