
from flask import Flask, render_template
from app import app

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/queue')
def queue():
  from app import db
  pkgs=["acl","attr"]
  return render_template('queue.html', packages = pkgs)

if __name__ == '__main__':
  app.run(debug=True)
