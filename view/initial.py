from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def success():
  return render_template('index.html')

# @app.route('/login',methods = ['POST', 'GET'])
# def login():
#   if request.method == 'POST':
#     print("FRANK: WAS POST METHOD")
#     user = request.form['nm']
#     return redirect(url_for('success',name = user))
#   else:
#     print("FRANK: WAS GET METHOD")
#     user = request.args.get('nm')
#     return redirect(url_for('success',name = user))

if __name__ == '__main__':
   app.run(debug = True)