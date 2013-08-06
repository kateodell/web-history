from flask import Flask, render_template, request
import model
import json

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
    data = site.get_data_for_display("num_images")
    return render_template("site_data.html", site=site, data=data)

@app.route('/analyze')
def display_all_queries():
     queries = model.session.query(model.Query).all()
     return render_template("analyze.html", queries=queries)

@app.route('/analyze/<query_name>')
def display_query(query_name):
    query = model.session.query(model.Query).filter_by(name=query_name).one()
    data = query.get_aggregate_data()
    return render_template("query_data.html", query=query, data=data)

@app.route('/api')
def get_api_data():
    url = request.args.get("site")
    query_name = request.args.get("query")
    # TODO add ability to specify a result format (avg, median, % that contain, etc)
    #result = request.args.get("result")

    if not query_name:
        return "ERROR - you must specify a query"
    query = model.session.query(model.Query).filter_by(name=query_name).first()
    if not query:
            return "ERROR - that query name does not exist"

    #  if a specific url is given, return the desired query data for that one site
    if url and url != "all":
        site = model.session.query(model.Site).filter_by(url=url).first()
        if not site:
            return "ERROR - that url does not exist"
        else:
            return site.get_data_for_display(query.name)
    else:  #if no site is specified, or "all" is specified as site, return aggregate data
        return json.dumps([{ 'data' : query.get_aggregate_data(), 'name':query.long_name, 'aggr_format':query.aggr_format }])


if __name__ == "__main__":
    app.run(debug=True)
