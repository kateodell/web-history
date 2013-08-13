from flask import Flask, render_template, request, redirect
import model
import json

from pyres import ResQ
resq = ResQ()

app = Flask(__name__)


@app.route('/')
def index():
    queries = model.get_all_queries()  # model.session.query(model.Query).all()
    return render_template("analyze.html", queries=queries)


@app.route('/sites')
def display_sites():
    sites = model.session.query(model.Site).all()
    urls = [s.url for s in sites]
    return render_template("sites.html", urls=urls)


@app.route('/sites/<site_name>')
def display_site(site_name):
    site = model.session.query(model.Site).filter_by(url=site_name).one()
    queries = model.session.query(model.Query).all()
    return render_template("site_data.html", site=site, queries=queries)


@app.route('/analyze')
def display_all_queries():
    queries = model.session.query(model.Query).all()
    return render_template("analyze.html", queries=queries)


@app.route('/analyze/<query_name>')
def display_query(query_name):
    query = model.session.query(model.Query).filter_by(name=query_name).one()
    return render_template("query_data.html", query=query)


@app.route('/new_query', methods=['GET','POST'])
def new_query():
    if request.method == 'GET':
        return render_template("new_query.html")
    else:  # method is POST
        tag_name = request.form['tag_name']
        query_type = request.form['query_type']
        q = model.add_new_query(tag_name, query_type)
        if q:
            resq.enqueue(model.Query, q.name)
            # q.run_query_on_all_sites()
            # q.aggregate_for_all_sites()
        return redirect("/analyze/"+query_type+"_"+tag_name)

@app.route('/about')
def display_about():
    return render_template('about.html')

@app.route('/api')
def get_api_data():
    url = request.args.get("site")
    query_name = request.args.get("query")
    # TODO add ability to specify a result format (avg, median, % that contain, etc)
    #result = request.args.get("result")

    # Error handling
    if not query_name:
        return "ERROR - you must specify a query", 400
    if query_name == "all":
        return json.dumps(model.get_all_queries())
    query = model.session.query(model.Query).filter_by(name=query_name).first()
    if not query:
            return "ERROR - that query name does not exist", 400

    #  if a specific url is given, return the desired query data for that one site
    if url and url != "all":
        site = model.session.query(model.Site).filter_by(url=url).first()
        if not site:
            return "ERROR - there is no data yet for that url", 400
        else:
            site_data = {'data':site.get_data_for_display(query.name), 'name':query.name, 'aggr_format':query.aggr_format}
            aggr_data = { 'data' : query.get_aggregate_data(), 'name':"All Sites"}
            return json.dumps([site_data, aggr_data])
    else:  # if no site is specified, or "all" is specified as site, return aggregate data
        return json.dumps([{ 'data' : query.get_aggregate_data(), 'name':'All Sites', 'title':query.aggr_format + " " + query.long_name}])


if __name__ == "__main__":
    app.run(debug=True)
