from flask import Flask, request, render_template, abort, redirect
import json

app = Flask(__name__)

@app.route('/')
def my_form():
    with open("config.json", "r") as f:
        config = str("".join(f.readlines()))
        return render_template('form.html', config=config)

@app.route('/', methods=['POST', 'GET'])
def my_form_post():
    text = request.form['text'].replace("'", "")
    with open("config.json", "w") as f:
        f.write(text)
    return redirect("/") 

app.debug = True
app.run()
