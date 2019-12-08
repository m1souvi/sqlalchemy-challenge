import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>"

    )

#########################################################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Retrieve the last 12 months of precipitation data"""
# Query for the dates and precipitation observations from the last 12 months.
    date_first = session.query(Measurement.date).order_by(Measurement.date).first().date
    date_last = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last12mths = dt.datetime.strptime(date_last, '%Y-%m-%d') - dt.timedelta(days=365)
    prcp_last12mths = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last12mths).\
        order_by(Measurement.date).all()

# Convert the query results to a Dictionary using date as the key and prcp as the value.
    prcp_totals = []
    for result in prcp_last12mths:
        row = {}
        row["date"] = prcp_last12mths[0]
        row["prcp"] = prcp_last12mths[1]
        prcp_totals.append(row)
        
# Return the JSON representation of your dictionary.
    return jsonify(prcp_totals)

#########################################################################################
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())

#########################################################################################
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for the last 12 months"""
# Query for the dates and temperature observations from a year from the last data point.
    date_last = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last12mths = dt.datetime.strptime(date_last, '%Y-%m-%d') - dt.timedelta(days=365)
    tobs_last12mths = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= last12mths).\
        order_by(Measurement.date).all()

# Convert the query results to a Dictionary using date as the key and tobs as the value.
    tobs_totals = []
    for result in tobs_last12mths:
        row = {}
        row["date"] = tobs_last12mths[0]
        row["tobs"] = tobs_last12mths[1]
        tobs_totals.append(row)

# Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(tobs_totals)

#########################################################################################
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def trip1(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    trip = list(np.ravel(trip_data))
    
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.
    return jsonify(trip)

#########################################################################################
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    trip_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    trip = list(np.ravel(trip_data))
    
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
    return jsonify(trip)

#########################################################################################

if __name__ == "__main__":
    app.run(debug=True)