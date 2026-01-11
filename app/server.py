from flask import Flask, render_template, jsonify, request,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from validators import url as url_validate
from HelperClass import EncoderDecoder
from datetime import datetime,timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_VALUE'] = 'sqlite:///shorty.db'
db = SQLAlchemy(app)
db.init_app(app)

with app.app_context():
    db.create_all()

helper = EncoderDecoder()
scheduler = APScheduler()

class Link(db.Model):
    short_code = db.Column(db.String(10), primary_key=True)
    long_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    clicks = db.Column(db.Integer, default=0)

@app.route('/')
def homePage():
    return render_template("homePage.html")

@app.route("/shorten",methods=['POST'])
def encodeUrl():
    data = request.get_json()

    longUrl = data.get('url','').strip()
    if longUrl and not longUrl.startswith(('http://', 'https://')):
        longUrl = 'https://' + longUrl
    if longUrl and url_validate(longUrl):
        shorten_code = helper.shortenUrl(longUrl)
        db.session.add(Link(shorten_code,longUrl))
        return jsonify({'shortUrl': "http://127.0.0.1:5000/" + shorten_code})
    else:
        return jsonify({'error': 'Invalid URL'}), 400

@app.route("/<short_code>",methods=['GET'])
def handleRedirect(short_code):
    longUrl = helper.getLongUrl(short_code)
    if longUrl:
        return redirect(longUrl)
    else:
        return render_template("InvalidRequest.html")

# Task to delete links older than 30 days
@scheduler.task('cron', id='delete_old_links', day='*')
def delete_expired_links():
    with app.app_context():
        expiration_date = datetime.now() - timedelta(days=30)
        Link.query.filter(Link.created_at < expiration_date).delete()
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)