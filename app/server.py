from flask import Flask, render_template

app = Flask(__name__)
@app.route('/')
def homePage():
    return render_template(template_name_or_list=["homePage.html"])

@app.route("/encodeUrl")
def encodeAndSave(url=""):
    return

if __name__ == "__main__":
    app.run(debug=True)