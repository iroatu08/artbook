#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)

# TODO: connect to a local postgresql database



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  venue_location = []
  set_venue_locations = db.session.query(Venue.state, Venue.city).group_by(Venue.state, Venue.city)
  
  for set_venue_location in set_venue_locations:
      venues = Venue.query.filter(Venue.state == set_venue_location.state).filter(Venue.city == set_venue_location.city).all()
      
      data=[]
      for venue in venues:
        data.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(db.session.query(Show).filter(Show.start_time > datetime.now()).all())
        })
        venue_location.append({
          "state": set_venue_location.state,
          "city": set_venue_location.city,
          "venues": data
        })
        
  return render_template('pages/venues.html', areas=venue_location)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  
  search_result = db.session.query(Venue).filter(Venue.name.like(f"%{search_term}%")).all()
  
  response={
    "count": len(search_result),
    "data": search_result
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get_or_404(venue_id)
  upcoming_shows_details = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
  
  prev_shows_details = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
  
  upcoming_shows=[]
  for show in upcoming_shows_details:
    upcoming_shows.append({
      'start_time': str(show.start_time),
      'artist_image_link': show.artist.image_link,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name 
      
    })
    
  past_shows=[]
  for show in prev_shows_details:
    past_shows.append({
      'start_time': str(show.start_time),
      'artist_image_link': show.artist.image_link,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name
      
    })
    
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error=False
    if request.method == 'POST':
      name= request.form['name']
      city= request.form['city']
      state= request.form['state']
      phone= request.form['phone']
      genres= request.form.getlist('genres')
      website_link= request.form['website_link']
      image_link= request.form['image_link']
      facebook_link= request.form['facebook_link']
      seeking_description=request.form['seeking_description']
      seeking_talent= True if request.form['seeking_talent'] == 'y' else False #convert the "y" returned by the form into a "True" to be saved to the database
      address= request.form['address']
      
      venue = Venue(name=name, city=city, address=address, genres=genres, state=state, phone=phone, website_link=website_link, image_link=image_link, facebook_link=facebook_link, seeking_description=seeking_description, seeking_talent=seeking_talent)
    
    try:
      db.session.add(venue)
      db.session.commit()
    except:
      error= True
      db.session.rollback()
      print(sys.exc_info())
    finally:
       db.session.close()
  # on successful db insert, flash success
    if error is False:
     flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
      flash('An error occurred. Venue ' +request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>/')
def delete_venue(venue_id):
  
  delete_venue = Venue.query.get_or_404(venue_id)
  try:
      db.session.delete(delete_venue)
      db.session.commit()
      flash ('Venue has been deleted successfully')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash ('Venue was not deleted successfully')
  finally:
    db.session.close()
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  search_result = db.session.query(Artist).filter(Artist.name.like(f"%{search_term}%")).all()
  response = {
      "count": len(search_result),
      "data": search_result
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get_or_404(artist_id)
  
  upcoming_shows_details = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time >= datetime.now()).all()
  
  prev_shows_details = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time <= datetime.now()).all()
  
  upcoming_shows=[]
  for show in upcoming_shows_details:
    upcoming_shows.append({
      'start_time': str(show.start_time),
      'venue_image_link': show.venue.image_link,
      'venue_id': show.venue.id,
      'venue_name': show.venue.name
      
    })
    
  past_shows=[]
  for show in prev_shows_details:
    past_shows.append({
      'start_time': str(show.start_time),
      'venue_image_link': show.venue.image_link,
      'venue_id': show.venue.id,
      'venue_name': show.venue.name
      
    })
   
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "state": artist.state,
    "city": artist.city,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get_or_404(artist_id)
  
  #populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  #take values from the form submitted, and update existing
  #artist record with ID <artist_id> using the new attributes
  error = False
  artist = Artist.query.get_or_404(artist_id)
  if request.method == 'POST':
         artist.name=request.form['name']
         artist.city=request.form['city']
         artist.state=request.form['state']
         artist.phone=request.form['phone']
         artist.genres=request.form.getlist('genres')
         artist.facebook_link=request.form['facebook_link']
         artist.image_link=request.form['image_link']
         artist.website=request.form['website_link']
         artist.seeking_venue= False if request.form['seeking_venue']== 'No' else True 
         artist.seeking_description=request.form['seeking_description']
  try:
    db.session.commit() 
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('Artist ' + request.form["name"] + 'was not updated successfully')
  else:
    flash("Updated Artist successfully")
  

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get_or_404(venue_id)
  #populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  #take values from the form submitted, and update existing
  #venue record with ID <venue_id> using the new attributes
  error = False
  venue=Venue.query.get_or_404(venue_id)
  if request.method == 'POST':
    venue.name= request.form['name']
    venue.city= request.form['city']
    venue.state= request.form['state']
    venue.phone= request.form['phone']
    venue.genres= request.form.getlist('genres')
    venue.website= request.form['website_link']
    venue.image_link= request.form['image_link']
    venue.facebook_link= request.form['facebook_link']
    venue.seeking_description= request.form['seeking_description']
    venue.seeking_talent= False if request.form['seeking_talent'] == 'No' else False
    venue.address= request.form['address']
  try:
    db.session.commit()
         
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
     db.session.close()
  if error:
     flash('Venue ' + request.form['name'] + 'was not edited successfully.')
  else: 
     flash("updated venue successfully")
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  #called upon submitting the new artist listing form
  #insert form data as a new Venue record in the db, instead
  #modify data to be the data object returned from db insertion
  error = False
  if request.method == 'POST':
    name= request.form['name']
    city= request.form['city']
    state= request.form['state']
    phone= request.form['phone']
    genres= request.form.getlist('genres')
    website_link= request.form['website_link']
    image_link= request.form['image_link']
    facebook_link= request.form['facebook_link']
    seeking_description=request.form['seeking_description']
    seeking_venue= True if request.form['seeking_venue'] == 'y' else False #converts the "y" returned by the form into a "True" to be saved to the database
    
    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, website_link=website_link, image_link=image_link,facebook_link=facebook_link,seeking_description=seeking_description,seeking_venue=seeking_venue)
      
  try:  
    db.session.add(artist)
    db.session.commit()
  except:
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
    flash('Artist ' + request.form["name"] + 'was not successfully listed.')
  else:
    flash("Artist " + request.form["name"] + " was successfully listed!")
  # on unsuccessful db insert, flash an error instead.
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data=[]
  shows = Show.query.join(Venue, Venue.id == Show.venue_id).join(Artist, Artist.id == Show.artist_id).all()
  for show in shows:
        data.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": str(show.start_time)
        })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  #called to create new shows in the db, upon submitting new show listing form
  #insert form data as a new Show record in the db, instead
  error = False
  if request.method == 'POST':
      artist_id = request.form['artist_id']
      venue_id= request.form['venue_id']
      start_time= request.form['start_time']
      show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      
  try:
      db.session.add(show)
      db.session.commit()
     
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      
  finally:
      db.session.close()
  if error:
    flash ('Show was not successfully listed')
    
  else:
     flash('Show was successfully listed!')
  #on unsuccessful db insert, flash an error instead.
  #flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
