from flask import Flask, render_template
from validators import url as url_validate
from HelperClass import EncoderDecoder

app = Flask(__name__)
@app.route('/')
def homePage():
    return render_template(template_name_or_list=["homePage.html"])

@app.route("/encodeUrl")
def encodeAndSave(URL=""):
    if url_validate(URL):
        pass
    else:
        pass

if __name__ == "__main__":
    app.run(debug=True)
    helper = EncoderDecoder