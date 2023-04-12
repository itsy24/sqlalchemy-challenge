# Import the dependencies.
import numpy as np
import sqlalchemy
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# Database Setup 
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Print all of the classes mapped to the Base 
Base.classes.keys()

# Save references to each table
measurement = Base.classes.measurement

station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#-----------------------------------------------
# Flask Setup
app = Flask(__name__)

# Flask Routes

#route 1 - welcome route
@app.route('/')
def welcome():
    return (
        f'Aloha! E como mai (welcome) to the Hawaii weather API! <br/>' 
        f'Available Routes: <br/>'
        f'/api/v1.0/precipitation <br/>'
        f'/api/v1.0/stations <br/>'
        f'/api/v1.0/tobs <br/>'
        f'/api/v1.0/yyyy-mm-dd <br/>'
        f'/api/v1.0/yyyy-mm-dd/yyyy-mm-dd'
    )

#route 2 - welcome
@app.route('/api/v1.0/precipitation')
#dictionary using date as the key and prcp as the value.
def precipitation():
    session = Session(engine)

    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    # Calculate the date one year from the last date in data set.
    prev_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d').date() - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    pcp_data = session.query(measurement.date,measurement.prcp).\
        filter(measurement.date >= prev_date).all()
    pcp_dict = {k:v for (k,v) in pcp_data}
    #return the JSON
    return jsonify ({'Date':'Precipitation in Inches'},pcp_dict)

#route 3 - stations in HI.
@app.route('/api/v1.0/stations')
#dictionary using date as the key and prcp as the value.
def stations():
    #start session -- conenct to db
    session = Session(engine)

    station_all = session.query(station.station).all()
    #return the JSON
                    #np.ravel turns the station_all tuple into a 1D list. 
    return jsonify (list(np.ravel(station_all)))

#route 4 - tobs - temperature of observation 
@app.route('/api/v1.0/tobs')
def tobs():
    #start session -- conenct to db
    session = Session(engine)

    #finds the most active station in hawaii
    most_active = session.query(measurement.station,func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    #find the most recent date
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    #find the last 12 months from the recent_dat
    prev_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d').date() - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    station_data = session.query(measurement.tobs,measurement.station).\
        filter(measurement.station == most_active[0][0]).\
        filter(measurement.date >= prev_date).all() 
    #return the JSON
    return jsonify (('Most Active Station TOBs Data'),list(np.ravel(station_data)))

#route 5 - start and ends date 
@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def date_temp(start = None, end = None):
    #start session -- conenct to db
    session = Session(engine)

    #converts user entry to date time format.
    start = dt.datetime.strptime(start, '%Y-%m-%d').date()
    
    #just have start date
    if not end:
        lowest_temp = session.query(func.min(measurement.tobs)).\
            filter(measurement.date >= start).scalar() 
            
        highest_temp = session.query(func.max(measurement.tobs)).\
            filter(measurement.date >= start).scalar()
        average_temp = session.query(func.round(func.avg(measurement.tobs)),2).\
            filter(measurement.date >= start).scalar()
        
        return jsonify({'Lowest Temperature':lowest_temp, 
                        'Highest Temperature': highest_temp, 
                        'Average Temperature' :average_temp})
    #start and end date
    end = dt.datetime.strptime(end, '%Y-%m-%d').date()

    lowest_temp = session.query(func.min(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).scalar()
    highest_temp = session.query(func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).scalar()
    average_temp = session.query(func.round(func.avg(measurement.tobs)),2).\
        filter(measurement.date >= start).filter(measurement.date <= end).scalar()
    return jsonify({'Lowest Temperature':lowest_temp, 
                        'Highest Temperature': highest_temp, 
                        'Average Temperature' :average_temp})


#start the app
if __name__ == "__main__":
    app.run(debug=True)