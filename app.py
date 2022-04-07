from flask import Flask, redirect, render_template, request
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from sqlalchemy import desc
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json




# initialiazing the flask app

app = Flask(__name__)
api = Api(app)



# Creating the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor.db'
db = SQLAlchemy(app)

# creating the UUID's
def generate_UUID():
    return "cac1010b-fa6e-4641-9d95-ba82ec4e5d27"


class Data(db.Model):
    uuid = db.Column(db.String(60), name = "uuid", nullable = False, primary_key = True)
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow, primary_key=True)
    decibel = db.Column(db.Integer, nullable = False)
# db.create_all()

# creating my request parser
sensor_post = reqparse.RequestParser()
sensor_post.add_argument("uuid",type = str, help = "This is required", default = generate_UUID, required = True)
sensor_post.add_argument("decibel",type = int, help= "This is Required", required = True)

# resource fields
resource_fields = {
    "uuid":fields.String,
    "timestamp": fields.DateTime,
    "decibel":fields.Integer
}


class Sensor(Resource):
    def get(self):
        datas = Data.query.all()
        all = []
        for data in datas:
            all.append ({"uuid":str(data.uuid), "timestamp":str(data.timestamp), "decibel":data.decibel})
        return all
    @marshal_with(resource_fields)
    def post(self):
        args = sensor_post.parse_args()
        sensor_new =Data(uuid = args['uuid'], decibel = args["decibel"])
        if args['uuid'] != generate_UUID():
            abort(405)
        db.session.add(sensor_new)
        db.session.commit()
        return sensor_new, 201

api.add_resource(Sensor, "/sensor")

@app.route('/')
def index():
    return render_template("login.html")
# login username and password
login_database = {"busayo":"busayo","admin":"admin","1234":"1234"}

# logging into the website
@app.route('/login', methods= ['GET', 'POST'])
def login():
    name = request.form['username']
    pwd = request.form['password']
    if name not in login_database:
        
        return render_template('login.html', info = 'User not found')
    else:
        if login_database[name]!= pwd:
            
            return render_template('login.html', info = 'incorrect password')
        else:
            return redirect('/home')

@app.route('/home', methods = ['GET','POST'])

def home():
    if request.method == 'GET':
        all_data = Data.query.order_by(desc(Data.timestamp)).all()
    return render_template("home.html", datas = all_data)

# running the flask app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="80")