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
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

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

@app.route('/jsonified')
def home():
    return jsonify({
        'routes': {
            '/precipitation': 'Precipitation data for the last year',
            '/stations': 'List of all stations',
            '/tobs': 'Temperature data for the most active station'
        }
    })


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)