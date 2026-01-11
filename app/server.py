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


def __updateHelper():
    all_links = Link.query.all()
    for link in all_links:
        helper.addLink(link.short_code,link.long_url)

with app.app_context():
    helper = EncoderDecoder()
    db.create_all()
    __updateHelper()

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
        shorten_url = helper.shortenUrl(longUrl)
        db.session.add(Link(short_code=shorten_url,long_url=longUrl))
        db.session.commit()
        return jsonify({'shortUrl': "http://127.0.0.1:5000/" + shorten_url})
    else:
        return jsonify({'error': 'Invalid URL'}), 400

@app.route("/<short_code>",methods=['GET'])
def handleRedirect(short_code):
    longUrl = helper.getLongUrl(short_code)
    if longUrl:
        link_record = Link.query.get(short_code)

        # Increment the counter
        link_record.clicks += 1
        # Save the change
        db.session.commit()

        return redirect(longUrl)
    else:
        return render_template("InvalidRequest.html")

# Task to delete links older than 30 days
@scheduler.task('cron', id='delete_old_links', day='*')
def delete_expired_links():
    with app.app_context():
        expiration_date = datetime.now() - timedelta(days=30)
        links_to_delete = Link.query.filter(Link.created_at < expiration_date).all()
        for link in links_to_delete:
            helper.deleteLink(link.short_code) #Remove from HashMap
            db.session.delete(link) #Remove from the Database
        db.session.commit()

if __name__ == "__main__":
    scheduler.init_app(app)  # Initialize the scheduler
    scheduler.start()  # Start the background tasks
    app.run(debug=True)