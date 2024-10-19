# Import the dependencies.
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, func
#Use automap_base() and reflect the database schema:
from sqlalchemy.ext.automap import automap_base
#Correctly create and bind the session between the Python app and database:
from sqlalchemy.orm import Session
import datetime as dt


#################################################
# Database Setup
#################################################

# Replace 'your_database.db' with the path to your SQLite database file
engine = create_engine('sqlite:///SurfsUp/Resources/hawaii.sqlite') 

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

#Correctly save references to the tables in the SQLite file (measurement and station):
Measurement = Base.classes.measurement
Station = Base.classes.station



# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Define the homepage route
@app.route('/')
def home():
    return (
        "Welcome to the Climate API!<br/>"
        "Available Routes:<br/><br/>"
        "/api/v1.0/precipitation - Precipitation data for the last year<br/>"
        "    Example: /api/v1.0/precipitation<br/><br/>"
        "/api/v1.0/stations - List of all stations<br/>"
        "    Example: /api/v1.0/stations<br/><br/>"
        "/api/v1.0/tobs - Temperature observations for the most active station in the last year<br/>"
        "    Example: /api/v1.0/tobs<br/><br/>"
        "/api/v1.0/<start> - Temperature statistics from the given start date to the most recent date.<br/>"
        "    Example: /api/v1.0/2013-01-01<br/><br/>"
        "/api/v1.0/<start>/<end> - Temperature statistics from the given start date to the given end date.<br/>"
        "    Example: /api/v1.0/2013-01-01/2015-12-02<br/>"
    )
    
# Define the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    try:
        # Get the most recent date from the dataset
        most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
        
        # Calculate the date 12 months before the most recent date
        last_12_months = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

        # Query for the precipitation data for the last 12 months
        precipitation_data = session.query(Measurement.date, Measurement.prcp)\
            .filter(Measurement.date >= last_12_months).all()

        # Handle case where no data is available
        if not precipitation_data:
            return jsonify({"message": "No precipitation data available for the last 12 months"})

        # Convert the query results to a dictionary with date as the key and precipitation as the value
        precipitation_dict = {date: prcp for date, prcp in precipitation_data}

        # Return the JSON representation of the dictionary
        return jsonify({
            "message": "The following data shows precipitation data for the last 12 months (365 days)",
            "data": precipitation_dict
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Close the session to avoid leaks
        session.close()

# Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    try:
        # Query all stations
        stations = session.query(Station.station).all()

        # Convert the query results into a list
        station_list = [station[0] for station in stations]
        return jsonify({
            "message": "The following data shows all the recorded stations",
            "data": station_list
        })
     # In case of invalid input information
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Close the session to avoid leaks
        session.close()

# Define the temperature observations (tobs) route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    try:
        # Query to get the most recent date
        most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
        
        # Calculate the last 12 months
        last_12_months = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
        
        # Query to get the most active station
        most_active_station = session.query(Measurement.station)\
            .group_by(Measurement.station)\
            .order_by(func.count(Measurement.station).desc())\
            .first()[0]

        # Query the dates and temperature observations for the most active station
        tobs_data = session.query(Measurement.date, Measurement.tobs)\
            .filter(Measurement.station == most_active_station)\
            .filter(Measurement.date >= last_12_months).all()

        # Handle case where no data is available
        if not tobs_data:
            return jsonify({"message": "No temperature data available for the most active station in the last 12 months"})

        # Convert the query results into a list of dictionaries
        tobs_list = [{"date": date, "tobs": tobs} for date, tobs in tobs_data]
        return jsonify({
            "message": "The following data shows the dates and temperature observations of the most-active station for the previous year of data.",
            "data": tobs_list
        })
    # In case of invalid input information
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Close the session
        session.close()

# Define the start route for calculating min, avg, and max temperatures
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    try:
        # Validate date format
        dt.datetime.strptime(start, '%Y-%m-%d')
        
        # Query to calculate min, max, and avg temperatures for all dates >= start
        temperature_stats = session.query(func.min(Measurement.tobs),
                                          func.max(Measurement.tobs),
                                          func.avg(Measurement.tobs))\
            .filter(Measurement.date >= start).all()

        # Handle case where no data is available
        if not temperature_stats[0][0]:
            return jsonify({"message": "No temperature data available for the given start date"})

        # Convert the query results into a dictionary
        stats_dict = {"TMIN": temperature_stats[0][0], "TAVG": temperature_stats[0][2], "TMAX": temperature_stats[0][1]}
        return jsonify({
            "message": "You can see MINIMUM, AVERAGE, and MAXIMUM temperature for the given Start DATE to the most recent data available",
            "data": stats_dict
        })
    # We added the proper format comment
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400
    # In case of invalid input information
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Close the session 
        session.close()

# Define the start-end route for calculating min, avg, and max temperatures
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    try:
        # Validate date format
        dt.datetime.strptime(start, '%Y-%m-%d')
        dt.datetime.strptime(end, '%Y-%m-%d')
        
        # Query to calculate min, max, and avg temperatures for dates between start and end
        temperature_stats = session.query(func.min(Measurement.tobs),
                                          func.max(Measurement.tobs),
                                          func.avg(Measurement.tobs))\
            .filter(Measurement.date >= start)\
            .filter(Measurement.date <= end).all()

        # Handle case where no data is available
        if not temperature_stats[0][0]:
            return jsonify({"message": "No temperature data available for the given date range"})

        # Convert the query results into a dictionary
        stats_dict = {"TMIN": temperature_stats[0][0], "TAVG": temperature_stats[0][2], "TMAX": temperature_stats[0][1]}
        return jsonify({
            "message": "You can see MINIMUM, AVERAGE, and MAXIMUM temperature from a given Start DATE to End DATE.",
            "data": stats_dict
        })

    # We added the proper format comment
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400
     # In case of invalid input information
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Close the session
        session.close()


# Run the Flask app
if __name__ == '__main__':
     app.run(port=8000, debug=True)