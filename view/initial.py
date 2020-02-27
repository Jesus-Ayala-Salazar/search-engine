from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)



@app.route('/results', methods = ['GET', 'POST'])
def results():
  query = request.args.get("query")
  print("get request of query: ", query)
  
  if query == '': #is empty
    return redirect('/')
  
  #res=somelookupfunction(query) #lst should now be tuples of (h1, link, sometext)
  res = [("Header1","https://en.wikipedia.org/wiki/Computer_programming", "text1text1text1text1text1text1text1text1"),\
    ("Header2","https://en.wikipedia.org/wiki/Computer_programming", "text2text2text2text2text2text2text2text2"), \
      ("Header3","https://en.wikipedia.org/wiki/Computer_programming", "text3text3text3text3text3text3text3text3"),\
        ("Header4","https://en.wikipedia.org/wiki/Computer_programming", "text4text4text4text4text4text4text4text4"), \
          ("Header5","https://en.wikipedia.org/wiki/Computer_programming", "text5text5text5text5text5text5text5text5")]
  return render_template("results.html", inputtedQuery = query, list_of_results = res)

@app.route('/', methods = ['GET', 'POST'])
def index():
  return render_template('index.html')

if __name__ == '__main__':
   app.run(debug = True)