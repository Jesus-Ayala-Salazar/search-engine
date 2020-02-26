
@app.route('/success/<query>', methods = ['GET', 'POST'])
def success(query):
  print("query:", query)
  return "Hello"
  
  

@app.route('/index', methods = ['GET'])
def index():
  print("get method")
  query = request.args.get('query')
  return redirect(url_for('success',name=query))
