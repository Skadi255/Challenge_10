# Import the dependencies.

import numpy as np
import flask 
print(flask.__version__)
import sqlalchemy
print(sqlalchemy.__version__)
import datetime as dt
from datetime import datetime
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
Base.prepare(autoload_with = engine)

# Save references to each table

measure = Base.classes.measurement
stations = Base.classes.station



# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

def str_date(date_str):
    format = '%Y-%m-%d'
    DM = datetime.strptime(date_str, format)

    return DM
 
session = Session(engine)

#Establish a global list with all acceptable dates 
date_range = session.query(measure.date).all()
date_range_list = []
for j in date_range:
    date_range_list.append(str_date(j[0]))

# Establishing a global Variable with the most active station most_act
station_act = session.query(measure.station, func.count(measure.station)).group_by(measure.station).order_by(func.count(measure.station).desc()).all()
session.close()
most_act = station_act[0][0]




#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():

    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/Y-M-D/start/<start><br/>"
        f"/api/v1.0/Y-M-D/starts/end/<starts>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    recent = session.query(measure.date).order_by(measure.date.desc()).first()
    recent_date = str_date(recent[0])
    query_date = recent_date - dt.timedelta(days=366)
    prcp_st = session.query(measure.date, measure.prcp).filter(measure.date >= query_date).filter(measure.prcp != None )

    session.close()
    
    prcp_data = []
    for date, prcp in prcp_st:
        prcp_dict = {}
        prcp_dict[f"{date}"] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)


@app.route("/api/v1.0/stations")
def stations_q():

    session = Session(engine)

    station_name = session.query(stations.station, stations.name)

    session.close()

    station_list = []
    for station, name in station_name:
        station_dict = {}
        station_dict["ID"] = station
        station_dict["name"] = name
        station_list.append(station_dict)

    return jsonify(station_list)    


@app.route("/api/v1.0/tobs")
def tobs_data():

    session = Session(engine)

    recent_sta = session.query(measure.date).filter(measure.station == most_act).order_by(measure.date.desc()).first()
    recent_st = str_date(recent_sta[0])
    m_act_date = recent_st - dt.timedelta(days=366)
    m_act_temp = session.query(measure.station, measure.date, measure.tobs).filter(measure.station == most_act).filter(measure.date >= m_act_date).all()

    session.close()

    tobs_list = []
    for stats, dates, tob_s in m_act_temp:
        tobs_dict = {}
        tobs_dict["station"] = stats
        tobs_dict["date"] = dates
        tobs_dict["tobs"] = tob_s
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/Y-M-D/start/<start>")
def fun_start(start):

    start_date = str_date(start)

    if start_date in date_range_list:

        session = Session(engine)
        temp_stats = session.query(func.min(measure.tobs), func.max(measure.tobs), func.avg(measure.tobs)).filter(measure.date >= start_date).all()
        session.close()

        min_mx_list = []
        min_mx_dict = {}
        min_mx_dict["min"] = temp_stats[0][0]
        min_mx_dict["max"] = temp_stats[0][1]
        min_mx_dict["avg"] = temp_stats[0][2]
        min_mx_list.append(min_mx_dict)

        return jsonify(min_mx_list)
        
    else:
        return (f"!!ERROR!! {start} is not in date range")
    

@app.route("/api/v1.0/Y-M-D/starts/end/<starts>/<end>")
def fun_start_end(starts, end):

    starts_date = str_date(starts)
    end_date = str_date(end)

    if (starts_date in date_range_list) and (end_date in date_range_list):

        session = Session(engine)
        temps_stats = session.query(func.min(measure.tobs), func.max(measure.tobs), func.avg(measure.tobs)).filter(measure.date >= starts_date).filter(measure.date <= end_date).all()
        session.close()

        min_mx_list2 = []
        min_mx_dict2 = {}
        min_mx_dict2["min"] = temps_stats[0][0]
        min_mx_dict2["max"] = temps_stats[0][1]
        min_mx_dict2["avg"] = temps_stats[0][2]
        min_mx_list2.append(min_mx_dict2)

        return jsonify(min_mx_list2)
        
    else:
        return (f"!!ERROR!! {start} is not in date range") 

if __name__ == '__main__':
    app.run(debug=True)