from flask import Flask, render_template, jsonify, request,redirect
from validators import url as url_validate
from HelperClass import EncoderDecoder

app = Flask(__name__)
helper = EncoderDecoder()

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
        return jsonify({'shortUrl': "http://127.0.0.1:5000/" + shorten_url})
    else:
        return jsonify({'error': 'Invalid URL'}), 400

@app.route("/<short_code>",methods=['GET'])
def handleRedirect(short_code):
    longUrl = helper.getLongUrl(short_code)
    if longUrl:
        return redirect(longUrl)
    else:
        return render_template("InvalidRequest.html")

if __name__ == "__main__":
    app.run(debug=True)