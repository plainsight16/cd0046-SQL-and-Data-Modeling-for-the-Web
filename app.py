#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
from ssl import ALERT_DESCRIPTION_UNKNOWN_PSK_IDENTITY
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import Venue, Artist, Show, db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    data = []
    venues = Venue.query.all()
    locations = set((venue.city, venue.state) for venue in venues)

    for location in locations:
        other_venue = Venue.query.filter(
            Venue.city == location[0] and Venue.state == location[1]).all()
        data.append({
            "city": location[0],
            "state": location[1],
            "venues": [{
                "id": other.id,
                "name": other.name,
                "num_upcoming_shows": Show.query.join(Venue).filter(Venue.id == Show.venue_id).filter(Show.start_time > datetime.utcnow()).count()
            } for other in other_venue]
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(venues),
        "data": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": Show.query.filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.utcnow()).count()
        } for venue in venues]
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    venue = Venue.query.get(venue_id)

    upcoming_shows = Show.query.join(Venue).filter(
        Venue.id == venue_id).filter(Show.start_time > datetime.utcnow())

    past_shows = Show.query.join(Venue).filter(
        Venue.id == venue_id).filter(Show.start_time <= datetime.utcnow())

    return render_template('pages/show_venue.html', venue=venue, upcoming_shows=upcoming_shows, past_shows=past_shows)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)

    add = request.form.get
    try:
        new_venue = Venue(name=add('name'), city=add('city'), state=add('state'), address=add('address'),
                          phone=add('phone'), genre=request.form.getlist('genres'), website_link=add('website_link'),
                          facebook_link=add('facebook_link'),
                          seeking_talent=form.seeking_talent.data,
                          seeking_description=add('seeking_description'))
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!')
        print("Success")
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    try:
        venue.delete()
        db.session.commit()
        flash(f'Venue {venue.name} has been successfully deleted')
    except:
        db.session.rollback()
        flash(f'Venue {venue.name} failed to delete')

    return redirect(url_for("index"))
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(artists),
        "data": [{
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": Show.query.filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.utcnow()).count()
        } for artist in artists]
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)

    upcoming_shows = Show.query.join(Artist).filter(
        Artist.id == artist_id).filter(Show.start_time > datetime.utcnow())

    past_shows = Show.query.join(Artist).filter(
        Artist.id == artist_id).filter(Show.start_time < datetime.utcnow())

    return render_template('pages/show_artist.html', artist=artist, upcoming_shows=upcoming_shows, past_shows=past_shows)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(
        name=artist.name,
        genres=artist.genres,
        city=artist.city,
        state=artist.state,
        phone=artist.phone,
        website=artist.website_link,
        facebook_link=artist.facebook_link,
        seeking_venue=artist.seeking_venue,
        seeking_description=artist.seeking_description,
        image_link=artist.image_link
    )
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    add = request.form.get
    form = ArtistForm(request.form)
    try:
        artist.name = add("name")
        artist.city = add("city")
        artist.state = add("state")
        artist.phone = add("phone")
        artist.image_link = add("image_link")
        artist.genres = request.form.getlist("genres")
        artist.facebook_link = add("facebook_link")
        artist.website_link = add("website_link")
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = add("seeking_description")
        db.session.commit()
    except:
        flash(f'An error occured please check the form and try again')
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(
        name=venue.name,
        genres=venue.genre,
        city=venue.city,
        address=venue.address,
        state=venue.state,
        phone=venue.phone,
        website=venue.website_link,
        facebook_link=venue.facebook_link,
        seeking_talent=venue.seeking_talent,
        seeking_description=venue.seeking_description,
        image_link=venue.image_link
    )
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    add = request.form.get
    form = VenueForm(request.form)
    try:
        venue.name = add("name")
        venue.city = add("city")
        venue.state = add("state")
        venue.address = add("address")
        venue.phone = add("phone")
        venue.image_link = add("image_link")
        venue.genre = request.form.getlist("genres")
        venue.facebook_link = add("facebook_link")
        venue.website_link = add("website_link")
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = add("seeking_description")
        db.session.commit()
    except:
        flash(f'An error occured please check the form and try again')
        print(sys.exc_info())
        db.session.rollback()
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
    add = request.form.get
    form = ArtistForm(request.form)

    try:
        new_artist = Artist(name=add("name"), city=add("city"), state=add("state"), phone=add("phone"), genres=request.form.getlist("genres"), image_link=add(
            "image_link"), facebook_link=add("facebook_link"), website_link=add("website_link"), seeking_venue=form.seeking_venue.data, seeking_description=add("seeking_description"))
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form["name"] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    data = []
    show_data = Show.query.all()
    for show in show_data:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.Venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.Artist.name,
            "artist_image_link": show.Artist.image_link,
            "start_time": show.start_time
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    add = request.form.get
    form = ShowForm(request.form)

    try:
        artist = Artist.query.get(add("artist_id"))
        venue = Venue.query.get(add("venue_id"))
        new_show = Show(start_time=add("start_time"))
        new_show.Artist = artist
        new_show.Venue = venue
        flash('Show was successfully listed!')
        db.session.add(new_show)
        db.session.commit()
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
