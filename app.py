from flask import Flask, render_template, request
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask_sqlalchemy import SQLAlchemy
import datetime

timer = datetime.datetime.now()

# initialiazing the flask app

app = Flask(__name__)
api = Api(app)

# class HelloWorld(Resource):
#     def get(self):
#         return{"data":"Helloworld"}
# class Helloname(Resource):
#     def get(self, name):
#         return{"data":"{}".format(name)}

# api.add_resource(HelloWorld, '/helloworld')
# api.add_resource(Helloname, "/helloworld/<string:name>")

# dictionary sensor data for temporary api testing 
sensordata = {
    1: {"timestamp":"yy-mm-dd-hh-mm-ss", "decibel":50},
    2: {"timestamp":"yyy-mmm-ddd-hhh-mmm-sss", "decibel":150},
    3: {"timestamp":"yyyy-mmmm-dddd-hhhh-mmmm-ssss", "decibel":250}
}
sensor_post = reqparse.RequestParser()
sensor_post.add_argument("uuid",type = str, help= "This is Required", required = True)
# sensor_post.add_argument("timestamp",type = str, help= "This is Required", required = True)
sensor_post.add_argument("timestamp",type = str, required = False)
sensor_post.add_argument("decibel",type = int, help= "This is Required", required = True)
#  getting all the sensor data

# Creating the database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor.db'
# db = SQLAlchemy(app)
# # creating the UUID's
# def generate_UUID():
#     return str(uuid.uuid4)

# class Data(db.Model):
#     id = db.Column(db.String(60), name = "uuid", primary_key=True, default = generate_UUID)
#     timestamp = db.Column(db.Time, unique = True)
#     decibel = db.Column(db.Integer, nullable = False)
# # db.create_all()

# test database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor.db'
db = SQLAlchemy(app)
# creating the UUID's
def generate_UUID():
    return str(uuid.uuid4)

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, name = "uuid", nullable = False, default = generate_UUID)
    timestamp = db.Column(db.String, unique = True)
    decibel = db.Column(db.Integer, nullable = False)
# db.create_all()

resource_fields = {
    "id": fields.Integer,
    "uuid":fields.String,
    "timestamp": fields.String,
    "decibel":fields.Integer
}


class Sensor(Resource):
    def get(self):
        datas = Data.query.all()
        all = {}
        for data in datas:
            all[data.id] = {"uuid":data.uuid, "timestamp":data.timestamp, "decibel":data.decibel}
        return all


class SensorData(Resource):
    # getting sensor data by ID
    @marshal_with(resource_fields)
    def get(self, sensor_id,uuid):
        data = Data.query.filter_by(id = sensor_id).first()
        if str(uuid)!= "abcde":
            abort(405)

        if not data:
            abort(404, "Couldn't find ID")
        
        return data

    # posting sensor data
    @marshal_with(resource_fields)
    def post(self, sensor_id, uuid):
        args = sensor_post.parse_args()
        # sensor_id = args["id"]
        # data = Data.query.filter_by(id = sensor_id).first()

        if str(uuid)!="abcde":
            abort(405)
        sensor_new =Data(id = sensor_id, uuid = args["uuid"], timestamp = args["timestamp"], decibel = args["decibel"])
        db.session.add(sensor_new)
        db.session.commit()
        return sensor_new, 201

    # Deleting sonsor data 
    # Not working I don't know why
  
    def delete(self, sensor_id,uuid):
        data = Data.query.filter_by(id = sensor_id).first()
        if str(uuid)!="abcde":
            abort(405)
        
        db.session.delete(data)
        return "Data deleted", 204
    
api.add_resource(SensorData, "/sensor/<int:sensor_id>/<string:uuid>")
api.add_resource(Sensor, "/sensor")

@marshal_with(resource_fields)
@app.route('/sensordata/<string:id>/<db>')
def recv_data(id, db):
    args = sensor_post.parse_args()
    
    if str(id) != "1234":
        abort(405)
    
    sensor_new = Data(id = args["id"], timestamp =timer , decibel = db)
    db.session.add(sensor_new)
    db.session.commit()
    return 201, sensor_new
    # return str(uuid) + " " + str(db)

@app.route('/')
def index():
    return render_template("login.html")
# login username and password
login_database = {"busayo":"busayo","admin":"admin","1234":"1234"}

# logging into the website
@app.route('/login', methods= ['GET', 'POST'])
def login():
    # if request.method== 'POST':
    name = request.form['username']
    pwd = request.form['password']
    if name not in login_database:
        
        return render_template('login.html', info = 'User not found')
    else:
        if login_database[name]!= pwd:
            
            return render_template('login.html', info = 'incorrect password')
        else:
            return render_template('home.html')



# running the flask app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="80")