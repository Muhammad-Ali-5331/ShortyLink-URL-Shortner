from flask import Flask, render_template, jsonify, request, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from validators import url as url_validate
from HelperClass import EncoderDecoder
from datetime import datetime,timedelta
from jose import jwt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shorty.db'
CLERK_PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlKnTkAkDx/30frlXhryk
Vb1dCgtOis/GftP6zgxmQStisLCynNerH6IiniZRMnxmCKaRTOLGyIMl1ha5WYnm
+dcEdGwSysFAcmc+E8q5eGr3Gm09/Fv/K/7BcfbxlvL02cyIGxnbNC7QtGJYqZGJ
Icaubj7VqQ69YRKaHjPQ8EYXStZazx13WGXDE3+8WjLEaK3OvSz1azgBdd+iN0bi
0dYXn0f3t/rS2xQyYiMFDX1l/qT34GOXCuotqVxajtG/2p5mqfuF/cgRVIgbD5sg
Ra85D9xCGPbrwLNetPOW+4mCjSCkHrVHc2f87lnbeUOr1j3tUJaabFHHvPb5iVj1
eQIDAQAB
-----END PUBLIC KEY-----
'''
db = SQLAlchemy(app)


class Link(db.Model):
    short_code = db.Column(db.String(10), primary_key=True)
    long_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.String(100), nullable=True)  # ID from Clerk
    clicks = db.Column(db.Integer, default=0)

def get_current_user():
    """Helper to verify Clerk JWT and return user_id"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        # Verify the token sent from your frontend
        payload = jwt.decode(
            token,
            CLERK_PUBLIC_KEY,
            algorithms=["RS256"],
            options={"verify_aud": False, "verify_at_hash": False}
        )
        return payload.get("sub") # This is the Clerk User ID
    except Exception as e:
        print(f"Auth error: {e}")
        return None

def __updateHelper():
    all_links = Link.query.all()
    for link in all_links:
        helper.addLink(link.short_code,link.long_url)

with app.app_context():
    helper = EncoderDecoder()
    db.create_all()
    __updateHelper()

scheduler = APScheduler()

@app.route('/')
def homePage():
    return render_template("homePage.html")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/shorten",methods=['POST'])
def shortenUrl():
    data = request.get_json()

    longUrl = data.get('url','').strip()
    user_id = get_current_user()

    # If no user_id is found, block the request
    if not user_id:
        return jsonify({
            'error': 'Authentication required',
            'message': 'Please sign in or create an account to shorten links.'
        }), 401

    if longUrl and not longUrl.startswith(('http://', 'https://')):
        longUrl = 'https://' + longUrl
    if longUrl and url_validate(longUrl):
        shorten_url = helper.shortenUrl(longUrl)
        db.session.add(Link(short_code=shorten_url,long_url=longUrl,user_id=user_id))
        db.session.commit()
        return jsonify({'shortUrl': request.host_url + shorten_url})
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

@app.route('/api/user-links', methods=['GET'])
def get_links():
    user_id = get_current_user()
    if not user_id:
        return jsonify({"links": []}), 401

    # Query your database for links where user_id matches
    user_links = Link.query.filter_by(user_id=user_id).all()

    return jsonify({
        "links": [{
            "shortCode": l.short_code,
            "shortUrl": request.host_url + l.short_code,
            "originalUrl": l.long_url,
            "clicks": l.clicks,
            "createdAt": l.created_at.isoformat()
        } for l in user_links]
    })


@app.route('/api/delete-link/<short_code>', methods=['DELETE'])
def delete_link(short_code):
    user_id = get_current_user()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    # Find the link and ensure it belongs to the current user
    link = Link.query.filter_by(short_code=short_code, user_id=user_id).first()

    if link:
        helper.deleteLink(short_code)  # Remove from HashMap helper
        db.session.delete(link)  # Remove from Database
        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'error': 'Link not found or unauthorized'}), 404

if __name__ == "__main__":
    scheduler.init_app(app)  # Initialize the scheduler
    scheduler.start()  # Start the background tasks
    app.run(debug=True)