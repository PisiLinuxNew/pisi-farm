
from flask import Flask, render_template
from app import app
from app import github
from app import gituser

@app.route('/')
def home():
  return render_template('home.html', user = gituser)

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/queue')
def queue():
  from app import db
  pkgs=["acl","attr"]
  return render_template('queue.html', packages = pkgs)

@app.route('/login')
def login():
  return github.authorize()

@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    next_url = request.args.get('next') or url_for('index')
    if oauth_token is None:
        flash("Authorization failed.")
        return redirect(next_url)

    user = User.query.filter_by(github_access_token=oauth_token).first()
    if user is None:
        user = User(oauth_token)
        db_session.add(user)
    gituser = str(github.get('user'))
    print "----",gituser
    user.github_access_token = oauth_token
    db_session.commit()
    return redirect(url_for('/'))

if __name__ == '__main__':
  app.run(debug=True)
