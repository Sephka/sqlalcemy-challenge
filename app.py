# Import Dependencies
from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.pool import StaticPool

# ◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘
# ◘      Database Setup      ◘
# ◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘
# Reference: https://stackoverflow.com/questions/33055039/using-sqlalchemy-scoped-session-in-theading-thread
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={"check_same_thread": False}, poolclass=StaticPool, echo=True)

# Reflect database
Base = automap_base()

# reflect tables
Base.prepare(engine, reflect=True)

# Save references to tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session from python to the database
session = Session(engine)

# Setup Flask
app = Flask(__name__)

# ◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘
# ◘       Flask Routes       ◘
# ◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘◘
# Home
@app.route("/")
def welcome():
        return """<html>
<h1>Hawaii Climate App (Flask API)</h1>
<img src="https://i.ytimg.com/vi/3ZiMvhIO-d4/maxresdefault.jpg" alt="Hawaii Weather"/>
<p>Precipitation Analysis:</p>
<ul>
  <li><a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></li>
</ul>
<p>Station Analysis:</p>
<ul>
  <li><a href="/api/v1.0/stations">/api/v1.0/stations</a></li>
</ul>
<p>Temperature Analysis:</p>
<ul>
  <li><a href="/api/v1.0/tobs">/api/v1.0/tobs</a></li>
</ul>
<p>Start Day Analysis:</p>
<ul>
  <li><a href="/api/v1.0/2017-03-14">/api/v1.0/2017-03-14</a></li>
</ul>
<p>Start & End Day Analysis:</p>
<ul>
  <li><a href="/api/v1.0/2017-03-14/2017-03-28">/api/v1.0/2017-03-14/2017-03-28</a></li>
</ul>
</html>
"""

# Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
  # Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
  
  # Calculate last years date from the last data point in the database
  last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
  
  # Create query to retrieve the last 12 months of precipitation data, selecting on 'date' and 'prcp' values
  prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).\
          order_by(Measurement.date).all()
  
  # Convert list of tuples into a dictionary
  prcp_data_list = dict(prcp_data)
  
  # Return the JSON representation of your dictionary.
  return jsonify(prcp_data_list)

# Station
@app.route("/api/v1.0/stations")
def stations():
  # Return a JSON list of stations from the dataset.
  stations_all = session.query(Station.station, Station.name).all()
  
  # Converts list of tuples into a list
  station_list = list(stations_all)
  
  # Returns JSON list of stations from data
  return jsonify(station_list)

# TOBS
@app.route("/api/v1.0/tobs")
def tobs():
  # Query for dates and temperature observations from a year from the last data point
  last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
  
  # Create query to retrieve the last 12 months of precipitation data selecting `date` and `prcp` values
  tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= last_year).\
    order_by(Measurement.date).all()
  
  # Convert list of tuples into normal list
  tobs_data_list = list(tobs_data)
  
  # Return JSON list of temperature observations (tobs) for the previous year
  return jsonify(tobs_data_list)

# Start Day
@app.route("/api/v1.0/<start>")
def start_day(start):
  start_day = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).group_by(Measurement.date).all()
  
  # Convert list of tuples into normal list
  start_day_list = list(start_day)
  
  # Return JSON list of min temp, avg temp and max temp for a given start range
  return jsonify(start_day_list)

# Start-End Day
@app.route("/api/v1.0/<start>/<end>")
def start_end_day(start, end):
  start_end_day = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
  
  # Convert list of tuples into normal list
  start_end_day_list = list(start_end_day)
 
  # Return JSON list of min temp, avg temp and max temp for a given Start-End range
  return jsonify(start_end_day_list)

# Define main behavior
if __name__ == '__main__':
  app.run(debug=True)