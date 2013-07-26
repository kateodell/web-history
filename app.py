from flask import Flask, render_template
import model

app = Flask(__name__)

@app.route('/')
def index():
    sites = model.session.query(model.Site).all()
    print "length of sites is ", len(sites)
    return render_template("index.html", sites=sites)

@app.route('/sites')
def display_sites():
     sites = model.session.query(model.Site).all()
     urls = [s.url for s in sites]
     return render_template("sites.html", urls=urls)

@app.route('/sites/<site_name>')
def display_site(site_name):
    site = model.session.query(model.Site).filter_by(url=site_name).one()
    data = site.get_data_for_display(None)
    return render_template("site_data.html", site=site, data=data)

@app.route('/analyze')
def display_all_queries():
     
     return render_template("analyze.html")

@app.route('/analyze/<query_name>')
def display_query(query_name):
    data = "this is some data about", query_name # need to get real data
    return render_template("query_data.html", name=query_name, data=data)



if __name__ == "__main__":
    app.run(debug=True)
