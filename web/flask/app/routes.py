from flask import Flask, render_template, jsonify
from app import app
from app import db

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/queue')
def queue():
  pkgs=["acl","attr"]
  return render_template('queue.html', packages = pkgs)

@app.route('/requestPkg')
def requestPkg():
  pkg = "acl"
  return pkg

@app.route('/parameter'):
  return jsonify(["docker-image": DOCKER_IMAGE, "dockerfile": DOCKERFILE])

if __name__ == '__main__':
  app.run(debug=True)
