from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from forms import *


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow,nullable=True)
    shows = db.relationship("Show", backref="venue", lazy=True, cascade="all, delete-orphan")
    
    def __init__(self, name, city, state, address, phone, image_link, facebook_link, genres, website_link, seeking_talent, seeking_description ):
      self.name = name
      self.city = city
      self.state = state
      self.address = address
      self.phone = phone
      self.image_link = image_link
      self.facebook_link = facebook_link
      self.genres = genres
      self.website_link = website_link
      self.seeking_talent = seeking_talent
      self.seeking_description = seeking_description
      
      def ___repr__(self):
        return f"{self.name}"
      
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    shows = db.relationship("Show", backref="artist", lazy=True, cascade="all, delete-orphan")
    
    def __init__(self, name, city, state, address, phone, image_link, facebook_link, genres, website_link, seeking_venue, seeking_description ):
      self.name = name
      self.city = city
      self.state = state
      self.address = address
      self.phone = phone
      self.image_link = image_link
      self.facebook_link = facebook_link
      self.genres = genres
      self.website_link = website_link
      self.seeking_venue = seeking_venue
      self.seeking_description = seeking_description
      
      def ___repr__(self):
        return f"{self.name}"


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'
  
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  
  def __init__(self, artist_id, venue_id, start_time, ):
      self.artist_id = artist_id
      self.venue_id = venue_id 
      self.start_time = start_time
     
      
      def ___repr__(self):
        return f"{self.artist_id}:{self.venue_id}:{self.start_time}"

  
 
