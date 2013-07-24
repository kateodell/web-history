from flask import Flask, render_template
import model

app = Flask(__name__)

@app.route('/')
def index():
    sites = model.session.query(model.Site).all()
    print "length of sites is ", len(sites)
    return render_template("index.html", sites=sites)





if __name__ == "__main__":
    app.run(debug=True)
