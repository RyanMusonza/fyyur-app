#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form, CSRFProtect
from forms import *
from flask_migrate import Migrate
from sqlalchemy import asc, desc

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate (app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

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
    genres = db.Column(db.ARRAY(db.String()))
    website_link = db.Column(db.String())
    looking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref=db.backref('Venue'), lazy=True, cascade='all, delete-orphan')


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String())
    looking_venues = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref=db.backref('Artist'), lazy=True)


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
  
  areas_data=[]

  areas = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

  # For loop to get the areas as per venues.html and grouping them by state and city 
  for area in areas:
    venue_data = []
    venues = Venue.query.filter_by(state = area.state).filter_by(city = area.city).all()

    # For loop to get the venues that have upcoming shows 
    for venue in venues:
      upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).all()

      # Mapping the data according to the mock data format
      venue_data.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(upcoming_shows) #Counting the number of shows retrieved from the upcoming_shows query
      })
    
    # Mapping the data according to the venues.html format
    areas_data.append({
      'city': area.city,
      'state': area.state,
      'venues': venue_data
    })
  
  return render_template('pages/venues.html', areas=areas_data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  search_term = request.form.get('search_term', '')
  # Query to get the results from the search allowing for case sensitive terms
  search_results = Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.name.ilike('%' + search_term + '%')).all()

  data = []

  # Going through the results to append the results according to the mock data format
  for search_result in search_results:

    upcoming_shows = db.session.query(Show).filter(Show.venue_id == search_result.id, Show.start_time > datetime.now()).all() #Not sure where this is used
    data.append({
      'id': search_result.id,
      'name': search_result.name,
      'num_upcoming_shows': len(upcoming_shows)
    })

  # Mapping the results according to the mock data format
  response={
    "count": len(search_results),
    "data": data
    }
  
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id) # Query to get the info of the venue using the specific venue id
  shows = Show.query.filter_by(venue_id=venue_id).order_by(Show.start_time.asc()).all() # Query to get all of the shows for the specific venue on the venue id
  
  upcoming_shows = []
  past_shows = []

  # Going through every show and mapping out the data according to the mock data format
  for show in shows:
    artist_name = Artist.query.with_entities(Artist.name).filter(Artist.id == show.artist_id).first() # Query to get the name of the venue using the show's venue id
    artist_image_link = Artist.query.with_entities(Artist.image_link).filter(Artist.id == show.artist_id).first() # Query to get the image link of the venue using the show's venue id
    show_data = {
      'artist_id': show.artist_id,
      'artist_name': artist_name[0],
      'artist_image_link': artist_image_link[0],
      'start_time': str(show.start_time)
    }

    #Adding the data acquired from the for loop to either upcoming shows or past shows depending on the start time
    if show.start_time > datetime.now():
      upcoming_shows.append(show_data)
    else:
      past_shows.append(show_data)

  # Mapping the venue data according to the mock data 

  venue_data = {
    'id': venue.id,
    'name': venue.name,
    'city': venue.city,
    'state': venue.state,
    'address': venue.address,
    'phone': venue.phone,
    'genres': venue.genres,
    'image_link': venue.image_link,
    'facebook_link': venue.facebook_link,
    'website': venue.website_link,
    'seeking_talent': True if venue.looking_talent in (True, 't', 'true') else False, #Ensuring the check box contains the correct bool from the database
    'seeking_description': venue.seeking_description,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows), # Function to get the number of past shows
    'upcoming_shows_count': len(upcoming_shows) # Function to get the number of upcoming shows
  }
    
  
  return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()

  # Assigning each field from the form to the respective columns in the venue database
  try:
    venue = Venue (
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      address = request.form['address'],
      phone = request.form['phone'],
      image_link = request.form['image_link'],
      facebook_link = request.form['facebook_link'],
      genres = request.form.getlist('genres'),
      website_link = request.form['website_link'],
      looking_talent = True if 'seeking_talent' in request.form else False,
      seeking_description = request.form['seeking_description']
    )

    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was successfully deleted!')
  
  except:
    db.session.rollback()
    flash('Deleting the venue encountered an issue')
  
  finally:
    db.session.close()
  
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=[]

  artists = Artist.query.with_entities(Artist.id, Artist.name).all()

  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  search_term = request.form.get('search_term', '')

  # Query to get the results from the search allowing for case sensitive terms
  search_results = Artist.query.with_entities(Artist.id, Artist.name).filter(Artist.name.ilike('%' + search_term + '%')).all()

  data = []
  
  # Going through the results to append the results according to the mock data format
  for search_result in search_results:

    upcoming_shows = db.session.query(Show).filter(Show.artist_id == search_result.id, Show.start_time > datetime.now()).all()
    data.append({
      'id': search_result.id,
      'name': search_result.name,
      'num_upcoming_shows': len(upcoming_shows) # Aggregated but not used anywhere on this page
    })

  # Mapping the results according to the mock data format
  response={
    "count": len(search_results), # Function to count the number of results returned
    "data": data
    }
  
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id) # Query to get the info of the artist using the specific artist id
  shows = Show.query.filter_by(artist_id=artist_id).order_by(Show.start_time.asc()).all() # Query to get all of the shows for the specific artist on the artist id
  
  upcoming_shows = []
  past_shows = []

  # Going through every show and mapping out the data according to the mock data format
  for show in shows:
    venue_name = Venue.query.with_entities(Venue.name).filter(Venue.id == show.venue_id).first() # Query to get the name of the venue using the show's venue id
    venue_image_link = Venue.query.with_entities(Venue.image_link).filter(Venue.id == show.venue_id).first() # Query to get the image link of the venue using the show's venue id
    show_data = {
      'venue_id': show.venue_id,
      'venue_name': venue_name[0],
      'venue_image_link': venue_image_link[0],
      'start_time': str(show.start_time)
    }

    #Adding the data acquired from the for loop to either upcoming shows or past shows depending on the start time
    if show.start_time > datetime.now():
      upcoming_shows.append(show_data)
    else:
      past_shows.append(show_data)

  # Mapping out the data for the artist that will be displayed
  artist_data = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website_link,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.looking_venues,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }

  
  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  # Query to get the details of the artist from the database using the artist id
  artist = Artist.query.filter(Artist.id == artist_id).first()

  # Populating the form with the artist info retrieved from the database
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.looking_venues
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()

  # Select query to get all the details of the artist from the database
  artist_edit = Artist.query.get(artist_id)

  try:
    # Updating the artist's details with those entered/changed in the Artist form
    artist_edit.name = request.form['name']
    artist_edit.city = request.form['city'] 
    artist_edit.state = request.form['state']
    artist_edit.phone = request.form['phone']
    artist_edit.genres = request.form.getlist('genres')
    artist_edit.image_link = request.form['image_link']
    artist_edit.facebook_link = request.form['facebook_link']
    artist_edit.website_link = request.form['website_link']
    artist_edit.looking_venues = True if 'seeking_venue' in request.form else False
    artist_edit.seeking_description = request.form['seeking_description']

    db.session.commit()
    flash('Artist: ' + request.form['name'] + ' details have been successfully changed!')
  except:
    db.session.rollback()
    flash('Artist: ' + request.form['name'] + ' details could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  # Query to get the details of the venue from the database using the venue id
  venue = Venue.query.filter(Venue.id == venue_id).first()

  # Populating the form with the venue info retrieved from the database
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.genres.data = venue.genres
  form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.looking_talent
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm()
  
  # Select query to get all the details of the venue from the database using venue id
  venue_edit = Venue.query.get(venue_id)

  # Updating the venue's details with those entered/changed in the Venue form
  try:
    venue_edit.name = request.form['name']
    venue_edit.city = request.form['city']
    venue_edit.state = request.form['state']
    venue_edit.address = request.form['address']
    venue_edit.phone = request.form['phone']
    venue_edit.image_link = request.form['image_link']
    venue_edit.facebook_link = request.form['facebook_link']
    venue_edit.genres = request.form.getlist('genres')
    venue_edit.website_link = request.form['website_link']
    venue_edit.looking_talent = True if 'seeking_talent' in request.form else False
    venue_edit.seeking_description = request.form['seeking_description']

    db.session.commit()
    flash('Venue: ' + request.form['name'] + ' details have been successfully changed!')

  except:
    db.session.rollback()
    flash('Venue: ' + request.form['name'] + ' details could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  
  # Assigning each field from the form to the respective columns in the artist table
  try:
    artist = Artist(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      image_link = request.form['image_link'],
      facebook_link = request.form['facebook_link'],
      website_link = request.form['website_link'],
      looking_venues = True if 'seeking_venue' in request.form else False,
      seeking_description = request.form['seeking_description']
    )

    # Inserting artist form details into the database
    db.session.add(artist)
    db.session.commit()
    flash('Artist: ' + request.form['name'] + ' was successfully listed!')
  
  except:
    db.session.rollback()
    flash('An error occurred. Artist: ' + artist.name + ' could not be listed.')
  
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data=[]

  # Query to get all of the info needed for shows using joins in ascending order of the start date only returning those with a start time later than the current time. Meaning past shows will not be displayed
  shows = db.session.query(Show.venue_id, Venue.name, Show.artist_id, Artist.name, Artist.image_link, Show.start_time).filter(Venue.id == Show.venue_id, Artist.id == Show.artist_id, Show.start_time > datetime.now()).order_by(Show.start_time.asc())

  # Going through all of the shows returned from the query and mapping them out in the format needed for the shows.html
  for show in shows:
    data.append({
      'venue_id': show[0],
      'venue_name': show[1],
      'artist_id': show[2],
      'artist_name': show[3],
      'artist_image_link': show[4],
      'start_time': str(show[5]) # Converting the start time to a string 
    }) 

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()

  # Assigning the data from the form to the respective fields in the Show table
  try:
    show = Show(
      start_time = request.form['start_time'],
      venue_id = request.form['venue_id'],
      artist_id = request.form['artist_id']
    )

    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
    
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
