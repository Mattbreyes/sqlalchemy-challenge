# Import the dependencies.
from flask import Flask, jsonify
import pandas as pd
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={"check_same_thread": False})

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(autoload_with = engine,reflect=True)

# Save references to each table

measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

###########################
# Repetitive functions
###########################


# find the latest date
def recent_date():
    
    # sort by descending and get the first value
    query = session.query(measurement).order_by(measurement.date.desc()).first()

      
    # access date through dictionary
    recenmydict = query.__dict__
    recent = recenmydict['date']

    # turn date from str into datetime
    # recent = pd.to_datetime(recent)
    return recent

# find date one year prior to latest date
def year_ago_date(date):
    
    # use function to find latest date:
    # latest = recent_date(date)
    date = pd.to_datetime(date)
    
    # find year ago date
    year_ago = date - dt.timedelta(days=365)
    
    return year_ago

# find the oldest date
def oldest_date():

    # sort by ascending and get the first value 
    query = session.query(measurement).order_by(measurement.date.asc()).first()
    
    # access date through dictionary
    oldest_dict = query.__dict__
    oldest = oldest_dict['date']

    # turn date from str into datetime
    oldest = pd.to_datetime(oldest)
    return oldest


# most active station
def most_active():

    # query to find the most active station
    query = session.query(measurement.station,func.count(measurement.station)).\
    group_by(measurement.station).order_by(func.count(measurement.station).desc())

    most_active_station = query[0][0]

    return most_active_station


def summary_stat(summary,start,date):

    # Empty list
    list = []

    # Construct and return dictionary
    for min, max, avg in summary:
        mydict = {}
        mydict["Start"] = start
        mydict["End"] = date
        mydict["TAVG"] = avg
        mydict["TMAX"] = max
        mydict["TMIN"] = min
        list.append(mydict)
    return list


#################################################
# Flask Routes
#################################################

# Home page 
@app.route("/")
def homepage():
    """List all available routes."""
    return(f"Home Page<br/>"
           f" <br/>"
           f"Available Routes:<br/>"
           f" <br/>"
           f"Route: /api/v1.0/precipitation<br/>"
           f"- Date and precipitation for latest year for all stations as JSON<br/>"
           f" <br/>"
           f"Route: /api/v1.0/stations<br/>"
           f"- List of unique stations as JSON<br/>"
           f" <br/>"
           f"Route: /api/v1.0/tobs<br/>"
           f"- Latest year of dates and temperatures for most active station<br/>"
           f" <br/>"
           f"Route: /api/v1.0/[start]<br/>"
           f"- Min, max, and avg temperature from start to latest date<br/>"
           f"- Replace [start] with date in YYYY-MM-DD format (no brackets)<br/>"
           f" <br/>"
           f"Route: /api/v1.0/[start]/[end]<br/>"
           f"- Min, max, and avg temperature for custom date range<br/>"
           f"- Replace [start] and [end] with date in YYYY-MM-DD format (no brackets)<br/>"
           )

################
# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
# Return as JSON
###############

@app.route("/api/v1.0/precipitation")
def precipitation():

    # query last year of data
    last_year = year_ago_date(recent_date())
    year_ago_query = session.query(measurement.date,measurement.prcp).\
    filter(measurement.date >= str(last_year)).all()
    

    # Convert each query result into a dictionary
    list = []
    for date,prcp in year_ago_query:
        prcp_dict = {date:prcp}
        list.append(prcp_dict)
    
    # Return json
    return jsonify(list)


##############
# Return a JSON list of stations from the dataset
##############


@app.route("/api/v1.0/stations")
def stations():

    # Query station table
    stations = session.query(station.station).distinct()

    # Convert query results into a list of unique stations
    station_list = [row[0] for row in stations]
    
    # Return json
    return jsonify(station_list)


###########
# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
###########

@app.route("/api/v1.0/tobs")
def tobs():

    # Query data from station
    last_year = year_ago_date(recent_date())
    query = session.query(measurement.date, measurement.tobs).\
    filter(measurement.date >= str(last_year)).filter(measurement.station == most_active()).all()

    # Extract date and tobs from each row in the query
    # Append station ID to show which station data is being shown
    results = []
    for i in query:
        d = dict(i)
        results.append(d)
        results.append(most_active())

    # Return json
    return jsonify(results)


#########
# Return a JSON list of the minimum temperature, the average temperature, 
# and the maximum temperature for a specified start or start-end range.
########

## Route for only start date provided
@app.route("/api/v1.0/<start>")
def start(start):

    # Try except for potential incorrect input
    try:

        # check if date is within range
        if str(recent_date()) < start or str(oldest_date()) > start:
            return 'error'
        
        else:

            # Check format YYYY-MM-DD
            dt.datetime.strptime(start,"%Y-%m-%d")

            # Query for summary
            summary = session.query(func.min(measurement.tobs),\
                                    func.max(measurement.tobs),\
                                    func.avg(measurement.tobs)).\
                                    filter(measurement.date >= start)

            # Return json
            return jsonify(summary_stat(summary,start,recent_date()))
        
    except:
        return 'error'


## Route for both start and end date provided
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):

    # Try except for correct input
    try:

        # check date range
        if str(recent_date()) < start or\
           str(oldest_date()) > start or\
           str(recent_date()) < end or\
           str(oldest_date()) > end or\
           start > end:
            return 'error'
        
        # Else
        else:

            # Check date formats YYYY-MM-DD
            dt.datetime.strptime(start,"%Y-%m-%d")
            dt.datetime.strptime(end,"%Y-%m-%d")


            # Query for stats
            summary = session.query(func.min(measurement.tobs),\
                                    func.max(measurement.tobs),\
                                    func.avg(measurement.tobs)).\
                                    filter(measurement.date >= start).\
                                    filter(measurement.date <= end)
            
            # Return json
            return jsonify(summary_stat(summary,start,end))

    except:
        return 'error'


if __name__ == '__main__':
    app.run(debug=True)

session.close()