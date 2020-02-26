from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

##TODO: 
  # 1. Post request for another token when list of results is already displayed


@app.route('/results', methods = ['GET', 'POST'])
def results():
  # print("in success function. Query:", query)
  # print("query:", query)
  # v  = request.form.get('someKey')
  
  resultForm = request.form
  query = request.form.get('query')
  if query == '': #is empty
    return redirect('/')
  
  print("resForm:", list(resultForm.items()))
  print("request type:", request.method)
  #lst=somelookupfunction(query) #lst should now be tuples of (h1, link, sometext)
  res = [("Header1","https://en.wikipedia.org/wiki/Computer_programming", "text1text1text1text1text1text1text1text1"),\
    ("Header2","https://en.wikipedia.org/wiki/Computer_programming", "text2text2text2text2text2text2text2text2"), \
      ("Header3","https://en.wikipedia.org/wiki/Computer_programming", "text3text3text3text3text3text3text3text3"),\
        ("Header4","https://en.wikipedia.org/wiki/Computer_programming", "text4text4text4text4text4text4text4text4"), \
          ("Header5","https://en.wikipedia.org/wiki/Computer_programming", "text5text5text5text5text5text5text5text5")]
  return render_template("results.html", inputtedQuery = query, list_of_results = res)

@app.route('/', methods = ['GET', 'POST'])
def index():
  return render_template('index.html')
  # if request.method == 'POST':
  #   print("index query is:", request.form['query'])
  #   q = request.form['query']
    
  #   return redirect(url_for('results',query = q))
  # else:
  #   print("get method")
    
  #   q = request.args.get('query')
  #   return redirect(url_for('success',query=q))



# @app.route('/success/<name>')
# def success(name):
#    return 'welcome %s' % name

# @app.route('/login',methods = ['POST', 'GET'])
# def login():
#    if request.method == 'POST':
#       print("post method")
#       user = request.form['nm']
#       return redirect(url_for('success',name = user))
#    else:
#       print("get method")
#       user = request.args.get('nm')
#       return redirect(url_for('success',name = user))

if __name__ == '__main__':
   app.run(debug = True)