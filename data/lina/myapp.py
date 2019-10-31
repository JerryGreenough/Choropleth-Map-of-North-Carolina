import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

engine = create_engine("postgresql://postgres:Helene@localhost:2903/project3")

# Reflect an existing database into a new model.
# Each table is reflected as a class.

Base = automap_base()

# Reflect the tables.

Base.prepare(engine, reflect=True)

NC_Counties = Base.classes['NC Drugs']

session = Session(engine)

#---------------------------------------------

# Go through the tables (other than the geometry table 'NC Counties'
# and extract the non-primary key columns for each of the datasets.

datasets = []
DBtables = {}

for xxx in Base.classes.keys():
	if xxx == 'NC Drugs': continue
	table = Base.classes[xxx]
	
	for aaa in table.__table__.columns:

		bbb = str(aaa).split(".")[1]
		if bbb != 'id':
			datasets.append(bbb)
			#datasets.append(bbb.replace("_", " "))
			DBtables[bbb] = table
			
			
# Create the names route. When called upon by the JavaScript code,
# this will populate the names route with a JSON string containing
# the names of the datatsets contained in the postgres DB.

county_data = session.query(NC_Counties).all()
			
@app.route("/names")
def names():
	"""Return a list of dataset names."""
	return jsonify(datasets)

#---------------------------------------------

@app.route("/")
def index():
	"""Return the homepage."""
	# The render_template function returns a string containing the
	# html required to render the page.
	return(render_template("index.html"))
	
#---------------------------------------------	
	
@app.route("/data/<datasetName>")
def QuantityData(datasetName):
	"""Return the data from the dataset associated with the given quantity + polygon info."""
	
	tableClass = DBtables[datasetName]
	tableData = session.query(tableClass).all()
	
	datadict = {}
	
	for xx in tableData:
		datadict[xx.id] = xx.__dict__[datasetName]
	
	data = []
	
	for cc in county_data:
		data.append({"name": cc.name, 
		"quantity": datadict[cc.id],
		"polygon":cc.boundary })
		
	jsonData = []
	jsonData.append(datasetName)
	jsonData.append(data)
	
	return jsonify(jsonData)

if __name__ == "__main__":
    app.run()