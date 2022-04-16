from flask import Flask, redirect, render_template, request, flash, session, url_for
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from sqlalchemy import desc
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime





# initialiazing the flask app

app = Flask(__name__)
api = Api(app)
app.secret_key = "flaskesp32"

# Creating the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor.db'
db = SQLAlchemy(app)

# creating the UUID's
def generate_UUID():
   return ["cac1010b-fa6e-4641-9d95-ba82ec4e5d27", "abcde"]


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
        if args['uuid'] not in generate_UUID():
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
    if request.method == 'POST':
        name = request.form['username']
        pwd = request.form['password']
        session['name'] = name
        session['pwd'] = pwd
        if name not in login_database:
            flash("User not found")
            return render_template('login.html')
        else:
            if login_database[name]!= pwd:
                flash("Incorrect password")
                return render_template('login.html')
            else:
                return redirect('/home')
    else:
        if 'name' and 'pwd' in session:
            return redirect(url_for('home'))
            
        return render_template('login.html')

@app.route('/logout')
def logout():
    if 'name' and 'pwd' in session:
        session.pop('name', None)
        session.pop('pwd', None)
        flash('You have been logged out!')

    return redirect(url_for('login'))

@app.route('/home')
def home():

    if 'name' and 'pwd' in session:
        # pagination
        page = request.args.get('page', 1, type=int)
        all_data = Data.query.order_by(desc(Data.timestamp)).paginate(page = page, per_page = 20)
        # top_data = Data.query.order_by(desc(Data.timestamp)).first()
        # print(dir(all_data))

        #for infinte scroll
        if 'hx_request' in request.headers:
            return render_template("table.html", datas = all_data)
        return render_template("home.html", datas = all_data)
    else:
        flash('Unauthorised access!')
        return redirect(url_for('login'))

# for active search
@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'name' and 'pwd' in session:
        # if methods == 'POST':
        search_table = request.args.get('search')
        if search_table:
            tables = Data.query.filter(Data.uuid.contains(search_table) | Data.timestamp.contains(search_table))
            
        else:
            tables = []
        # return render_template('search.html', result = tables)
            
        if 'hx_request' in request.headers:
            return render_template("searchres.html", result = tables)
        return render_template('search.html', result = tables)
    else:
        flash('Unauthorised access!')
        return redirect(url_for('login'))

# for average
def get_average(a,w):
    if a and w:
        a = int(a)
        last_data = Data.query.filter_by(uuid = w).order_by(desc(Data.timestamp)).limit(a * 60).all()
        divider = len(last_data)
        num = 0
        for last in last_data:
            num = num + last.decibel
        if divider != 0:
            average = num/divider
            return int(average)
        flash("Incorrect UUID")
@app.route('/average')
def average():
    if 'name' and 'pwd' in session:
        # per hour
        a = request.args.get('a')
        uuid1 = request.args.get('uuid')
        average1 = get_average(a,uuid1)
        if average1:
            return render_template('average.html', avg = average1)
        # per day
        n = request.args.get('n')
        uuid2 = request.args.get('uuid2')
        average2 = get_average(n, uuid2)
        if average2:
        # print(int(average))
        # if 'hx_request' in request.headers:
        #     return render_template('avg.html', avg = average)
            return render_template('average.html', avn = average2)
            
        # per week
        w = request.args.get('w')
        uuid2 = request.args.get('uuid2')
        average3 = get_average(w,uuid2)
                # print(int(average))
        # if 'hx_request' in request.headers:
        #     return render_template('avg.html', avg = average)
        if average3:
            return render_template('average.html', avw = average3)
        return render_template('average.html')
    else:
        flash('Unauthorized access!')
        return(redirect(url_for('login')))

# running the flask app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="80")
