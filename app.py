from operator import and_
from os import abort
from flask import Flask, render_template, request, redirect
from flask.helpers import flash, url_for
from sqlalchemy.sql.operators import op
from sqlalchemy import func, distinct, select
from werkzeug.utils import secure_filename
from models import FilterModel, db
import urllib.parse
import csv
import copy
import os
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
import time
import redis
from flask_googlecharts import GoogleCharts
from flask_googlecharts import BarChart


# r = redis.StrictRedis(host='asnmt.redis.cache.windows.net',
#                       port=6380, db=0, password='sx66F5U7vVjPUddO04KTLFDptrbzUAm29ahkUX048Eg=', ssl=True)


table_creation_time = '0.82 seconds'

app = Flask(__name__)  # define app
app.secret_key = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # sqlite file
# disable sqlalchemy event system
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/'  # path to upload folder
db.init_app(app)  # initialize app

charts = GoogleCharts(app)
charts.init_app(app)
my_chart = BarChart("my_chart", options={'title': 'My Chart'})
my_chart.add_column("string", "Asd1")
my_chart.add_column("string", "Asd2")
my_chart.add_rows([["qwe1", 1], ["qwe2", 2], ["qwe3", 3], ])
# executed before first request


@app.before_first_request
def create_table():
    db.create_all()  # create all tables


# base url
@app.route('/')
def home():
    return render_template('index.html', table_creation_time=table_creation_time)

# SQL random query




# SQL restricted query
@app.route('/piechart', methods=['GET', 'POST'])
def piechart():
    if request.method == 'POST':
        lower = request.form['lower']
        upper = request.form['upper']
        earthquakes = []
        if upper != '' and lower != '':
            start1 = time.time()
            earthquakes = FilterModel.query.filter((FilterModel.mag != '') & (
                FilterModel.mag <= upper) & (FilterModel.mag >= lower))
            end1 = time.time()
            time_taken1 = end1 - start1
        if earthquakes:
            return render_template('chart.html', earthquakes=earthquakes, count=earthquakes.count(), time_taken1=time_taken1, labels=[i.time for i in earthquakes], values1=[i.mag for i in earthquakes], values2=[i.depth for i in earthquakes], datasets='1')


# Redis random query
@app.route('/linechart', methods=['GET', 'POST'])
def linechart():
    if request.method == 'POST':
        lower = request.form['lower']
        upper = request.form['upper']
        earthquakes = []
        if upper != '' and lower != '':
            start1 = time.time()
            earthquakes = FilterModel.query.filter((FilterModel.mag != '') & (
                FilterModel.mag <= upper) & (FilterModel.mag >= lower)).order_by(FilterModel.time.desc()).limit(100)
            end1 = time.time()
            time_taken1 = end1 - start1
        if earthquakes:
            return render_template('chart.html', earthquakes=earthquakes, count=earthquakes.count(), time_taken1=time_taken1, labels=[i.time for i in earthquakes], values1=[i.mag for i in earthquakes], values2=[i.depth for i in earthquakes], datasets='2')


# Redis restricted query
@app.route('/results/earthquakebymag2', methods=['GET', 'POST'])
def results_4():
    if request.method == 'POST':
        lower = request.form['lower']
        upper = request.form['upper']
        results_list = []
        key_list = []
        if upper != '' and lower != '':
            start1 = time.time()
            for i in range(1000):
                key_list = r.zrangebyscore('mag', lower, upper)
            end1 = time.time()
            time_taken1 = end1 - start1
            for key in key_list:
                rec = r.hgetall(key)
                results_list.append(rec)

        return render_template('chart.html', earthquakes=results_list, count=len(results_list), time_taken1=time_taken1)


# Your assignment is to provide a local interface (using a web page, displayed in a    browser) to a cloud service that you will implement that will allow a user to upload     earthquake data and investigate it.
# insert data into database via csv file
@app.route('/data/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.host_url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.host_url)
        if file:  # check file extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(
                file.filename)))  # save file to server
            with open("static/uploads/" + file.filename, newline='') as f:
                reader = csv.reader(f, delimiter=',')
                cont = True
                filter_list = []
                ctr = 0
                for row in reader:
                    if cont:  # ignore first row of table headers
                        cont = False
                        continue
                    if row[14] != "earthquake":  # check if type is earthquake
                        continue
                    # format time string to datetime
                    formatted_time = datetime.strptime(
                        row[0], '%Y-%m-%dT%H:%M:%S.%fZ')
                    # save data to a model
                    filter = FilterModel(time=formatted_time, latitude=float(row[1] if row[1] else 0), longitude=float(row[2] if row[2] else 0), depth=float(row[3] if row[3] else 0), mag=float(row[4] if row[4] else 0), magType=row[5], nst=row[6], gap=row[
                                         7], dmin=row[8], rms=row[9], net=row[10], id=row[11], updated=row[12], place=row[13], type=row[14], horizontalError=row[15], depthError=row[16], magError=row[17], magNst=row[18], status=row[19], locationSource=row[20], magSource=row[21])
                    filter_list.append(filter)

                    record = {'time': row[0], 'latitude': float(row[1] if row[1] else 0), 'longitude': float(
                        row[2] if row[2] else 0), 'depth': float(row[3] if row[3] else 0), 'mag': float(row[4] if row[4] else 0)}

                    p = r.pipeline()
                    p.hmset(row[0], record)
                    p.zadd('mag', {row[0]: record['mag']})
                    p.execute()

                db.session.bulk_save_objects(filter_list)
                db.session.commit()  # write to database
            flash("Successfully added new records.")
            return render_template('index.html')


# show all records
@app.route('/data', methods=['GET', 'POST'])
def RetrieveList():
    earthquakes = FilterModel.query.filter(FilterModel.pr_id >= 1)
    return render_template('chart.html', earthquakes=earthquakes, count=earthquakes.count())

# delete all records


@app.route('/data/delete', methods=['GET', 'POST'])
def DeleteAll():
    db.session.query(FilterModel).delete()
    db.session.commit()
    r.flushall()
    flash("Successfully deleted all records.")
    return render_template('index.html')


if __name__ == '__main__':
    app.run()  # begin application
