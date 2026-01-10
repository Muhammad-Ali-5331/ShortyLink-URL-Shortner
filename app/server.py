from flask import Flask, render_template,jsonify
from validators import url as url_validate
from HelperClass import EncoderDecoder
app = Flask(__name__)
helper = EncoderDecoder()
@app.route('/')
def homePage():
    return render_template(template_name_or_list=["homePage.html"])

@app.route(path="/shorten",methods=['POST'])
def encodeUrl(URL):
    if url_validate(URL):
        shorten_url = helper.shortenUrl(URL)
        return jsonify({'shortUrl':"https://linkey.it/"+ shorten_url})
    else:
        return jsonify({'error': 'Invalid URL'}), 400

if __name__ == "__main__":
    app.run(debug=True)