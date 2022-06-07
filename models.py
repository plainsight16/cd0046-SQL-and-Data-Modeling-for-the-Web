import datetime
from email.policy import default
from enum import unique
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    start_time = db.Column(db.DateTime(), nullable=False)

    def __str__(self) -> str:
        return f'Name: {self.name}'


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genre = db.Column(db.ARRAY(db.String(100)), default=[])
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500), default=None)
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String())
    date_created = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    shows = db.relationship('Show', backref='Venue', lazy=True)

    def __str__(self) -> str:
        return f'Name: {self.name}'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), default=[])
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(200))
    shows = db.relationship('Show', backref='Artist', lazy=True)

    def __str__(self) -> str:
        return f'Name: {self.name}'
