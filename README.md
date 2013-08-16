web-history
===========

final project for hackbright - IN PROGRESS

Overview
-----------

This is a webapp that calculates and displays historical analysis of how HTML tag usage has changed over time. It was built with Python using the Flask framework. Postgresql and Redis are used to store the data. On the front end, I used jQuery, Bootstrap, and Rickshaw.js. The calculations are based on content from the Internet Archive's Wayback Machine (http://archive.org/web/web.php)

Getting the Raw Data (get_data.py)
---------------------

I used the Wayback Machine's API to get the list of available capture dates for each site (parsing the JSON response to get all available timestamps). Using the timestamps

Databases (model.py)
--------------------

This app uses both a Postgresql database and a Redis database.

The Postgresql database stores the raw data and query information. SQLAlchemy is used as the ORM to manage the database w/ Python. There are 3 tables (which each map to a class in model.py)
* Site: The sites table has a row for each site data has been collected for
* Capture: The captures table has a row for each capture (a snapshot of a particular site and a particular point in time). There is a column that stores the raw text for each particular capture. This raw text is what is analyzed to calculate each query.
* Query: The queries table has a row for each unique type of query that can be run. There are multiple types of queries that can be run that have differing ways of calculating the query results. Each type of query is a subclass of the base Query class.

The Redis database is used to store the results of the query calculations for each site, as well as the aggregated data for each query.  To display the data, the webapp is primarily making requests to the Redis database, not Postgres.


Web App (app.py)
------------------

This app is written in Python using the Flask framework.

The app contains an API route that returns a JSON string of the data points needed to display a specific query in a Rickshaw graph.


Front End (static/templates folders)
-------------------------------------

Flask template pages, jQuery, [Rickshaw.js](http://code.shutterstock.com/rickshaw/) for displaying the graphs.

