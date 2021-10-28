
from enum import unique
from flask_sqlalchemy import SQLAlchemy

db =SQLAlchemy()
 

class FilterModel(db.Model):
    __tablename__ = "filter"

    pr_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    time = db.Column(db.DateTime)
    latitude = db.Column(db.Text)
    longitude = db.Column(db.Text)
    depth = db.Column(db.Text)
    mag = db.Column(db.Text)
    magType = db.Column(db.Text)
    nst = db.Column(db.Text)
    gap = db.Column(db.Text)
    dmin = db.Column(db.Text)
    rms = db.Column(db.Text)
    net = db.Column(db.Text)
    id = db.Column(db.Text)
    updated = db.Column(db.Text)
    place = db.Column(db.Text)
    type = db.Column(db.Text)
    horizontalError = db.Column(db.Text)
    depthError = db.Column(db.Text)
    magError = db.Column(db.Text)
    magNst = db.Column(db.Text)
    status = db.Column(db.Text)
    locationSource = db.Column(db.Text)
    magSource = db.Column(db.Text)
									
    def __init__(self,time,latitude,longitude,depth,mag,magType,nst,gap,dmin,rms,net,id,updated,place,type,horizontalError,depthError,magError,magNst,status,locationSource,magSource):
        # self.pr_id = pr_id
        self.time = time
        self.latitude = latitude
        self.longitude = longitude
        self.depth = depth
        self.mag = mag
        self.magType = magType
        self.nst = nst
        self.gap = gap
        self.dmin = dmin
        self.rms = rms
        self.net = net
        self.id = id
        self.updated = updated
        self.place = place
        self.type = type
        self.horizontalError = horizontalError
        self.depthError = depthError
        self.magError = magError
        self.magNst = magNst
        self.status = status
        self.locationSource = locationSource
        self.magSource = magSource

    def __repr__(self):
        return f"'mag':{self.mag},'depth':{self.depth},'time':{self.time},'place':{self.place},'longitude':{self.longitude},'latitude':{self.latitude},"

