from flask import render_template, flash, request, redirect, send_file, make_response, session, url_for
from . import app
from .models import User, Admin, Album, Playlist, Song
from . import db, bcrypt
import io

# admin = Admin(username='admin', password=bcrypt.generate_password_hash('admin@123', 10))
# db.session.add(admin)
# db.session.commit()

def get_current_user():
    # Get the user ID from the session
    user_id = session.get('user_id')

    if user_id:
        # Retrieve the user from the database using the ID
        return User.query.get(user_id)

    return None



# MAIN INDEX FILE
@app.route('/')
def index():
    return render_template('index.html', title = '')

# ADMIN LOGIN
@app.route('/admin/', methods=['POST', 'GET'])
def adminIndex():
    # CHECK IF REQUEST IS POSTED OR NOT
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == '' and password == '':
            flash("Please enter all the details!", 'danger')
            return redirect('/admin/')
        else:
            # ADMINS SHOULD LOGIN BY USERNAME
            admins = Admin().query.filter_by(username=username).first()
            if admins and bcrypt.check_password_hash(admins.password, password):
                session['admin_id'] = admins.id
                session['admin_name'] = admins.username
                return redirect('/admin/dashboard')
            else:
                flash("Invalid username and password!", 'danger')
                return redirect('/admin/')
    else:
        return render_template('admin/index.html', title = 'Admin Login')



# ADMIN DASHBOARD
@app.route('/admin/dashboard')
def adminDashboard():
    if not session.get('admin_id'):
        return redirect('/admin/')
    users = User.query.all()
    return render_template('/admin/dashboard.html', title="Admin Dashboard", users=users)


# ADMIN LOGOUT
@app.route('/admin/logout')
def adminLogout():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if session.get('admin_id'):
        session['admin_id'] = None
        session['admin_name'] = None
        flash("Logged Out Successfully! Login again to enter", 'danger')
        return redirect('/')

# ADMIN GET ALL ALBUMS
@app.route('/admin/all-albums', methods=["POST","GET"])
def adminGetAllAlbums():
    albums = Album.query.all()
    return render_template('/admin/all-albums.html', albums=albums)

# DELETE ALBUM
@app.route('/admin/deleteAlbum/<int:album_id>')
def delete_album_admin(album_id):
    album = Album.query.get(album_id)
    if album:
        db.session.delete(album)
        db.session.commit()
    return redirect(url_for('adminGetAllAlbums'))

# DELETE SONG
@app.route('/admin/deleteSong/<int:song_id>')
def delete_song_admin(song_id):
    song = Song.query.get(song_id)
    if song:
        db.session.delete(song)
        db.session.commit()
    return redirect(url_for('adminGetAllAlbums'))

# --------- USER ---------

#USER LOGIN
@app.route('/user/', methods=['POST', 'GET'])
def userIndex():
    if session.get('user_id'):
        print(session)
        return redirect('/user/userDashboard')
    if request.method == 'POST':
        # GET THE NAME OF THE FIELD
        email = request.form.get('email')
        password = request.form.get('password')

        #CHECK USER EXISTS OR NOT
        users = User().query.filter_by(email=email).first()
        if users and users.blacklist:
            flash("You are blacklisted!", 'danger')
            return redirect('/user/')
        if users and bcrypt.check_password_hash(users.password, password):
            session['user_id'] = users.id
            session['username'] = users.username
            return redirect('/user/userDashboard')
        else:
            flash("Please check email or password!", 'danger')
            return redirect('/user/')
    else:
        return render_template('user/index.html', title = 'User Login')


#USER REGISTRATION
@app.route('/user/signup', methods=['POST', 'GET'])
def userSignup():
    if session.get('user_id'):
        return redirect('/user/userDashboard')
    if request.method == 'POST':
        # GET ALL INPUT FIELDS NAME
        name = request.form.get('name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # CHECK ALL THE FIELDS ARE ENTERED OR NOT
        if name == '' or email == '' or username == '' or password == '':
            flash("Please enter all the fields!", 'danger')
            return redirect('/user/signup')
        else:
            is_email = User().query.filter_by(email=email).first()
            if is_email:
                flash("Email already exists!", 'danger')
                return redirect('/user/signup')
            else:
                hash_password = bcrypt.generate_password_hash(password, 10)
                user = User(name=name, email=email, username=username, password=hash_password)
                db.session.add(user)
                db.session.commit()
                flash("Account Creation Successful! Login again to enter", 'success')
                return redirect('/user/')
    else:
        return render_template('user/signup.html', title = 'User Signup')

# USER LOGOUT
@app.route('/user/logout')
def userLogout():
    if session.get('user_id'):
        session['user_id'] = None
        session['username'] = None
        flash("Logged Out Successfully! Login again to enter", 'danger')
        return redirect('/')


# USER DASHBOARD
@app.route('/user/userDashboard')
def userDashboard():
    current_user = get_current_user()
    songs = Song.query.all()
    albums = Album.query.all()
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    genres = db.session.query(Song.genre).distinct().all()
    all_genres = [genre[0] for genre in genres]
    creators = User.query.filter_by(is_creator=1).all()
    return render_template('/user/userDashboard.html', songs=songs, albums=albums, playlists=playlists, include_musicplayer=True, creators=creators, all_genres=all_genres, username=current_user.name)

# USER - SEARCH
@app.route('/user/search', methods=['POST'])
def search():
    current_user = get_current_user()
    search_query = request.form.get('search')
    songs = Song.query.filter(Song.title.ilike(f"%{search_query}%")).all()
    albums = Album.query.filter(Album.title.ilike(f"%{search_query}%")).all()
    creators = User.query.filter(User.name.ilike(f"%{search_query}%"), User.is_creator == 1).all()
    return render_template('user/search.html', songs=songs, search_query=search_query, albums=albums, creators=creators, include_musicplayer=True, username=current_user.name)

# GET COVER
@app.route('/album_cover/<int:album_id>')
def get_album_cover(album_id):
    album = Album.query.get(album_id)
    if album and album.cover:
        return send_file(io.BytesIO(album.cover), mimetype='image/jpg')
    else:
        return send_file('path/to/placeholder.jpg', mimetype='image/jpeg')

# GET COVER - MUSIC PLAYER
@app.route('/album_cover_player/<int:songId>')
def get_album_cover_musicPlayer(songId):
    song = Song.query.get(songId)
    albumId = song.album_id
    album = Album.query.get(albumId)
    if album and album.cover:
        return send_file(io.BytesIO(album.cover), mimetype='image/jpg')
    else:
        return send_file('path/to/placeholder.jpg', mimetype='image/jpeg')
        
# GET PROFILE PIC
@app.route('/profile_pic/<int:user_id>')
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if user and user.profile:
        return send_file(io.BytesIO(user.profile), mimetype='image/jpeg')
    else:
        return send_file('path/to/placeholder.jpg', mimetype='image/jpeg')

#USER GET SONGS
@app.route('/get_song/<int:song_id>')
def get_song(song_id):
    song = Song.query.get(song_id)
    if song:
        response = make_response(song.file_data)
        response.headers.set('Content-Type', 'audio/mpeg')
        return response
    return "Song not found", 404


# USER - CREATOR
@app.route('/user/Creator/existCreator')
def creator():
    current_user = get_current_user()

    if current_user and current_user.is_creator:
        return render_template('/user/Creator/existCreator.html', csspage='/static/existcreat.css', username=current_user.name)
    else:
        return redirect('/user/Creator/newCreator')

# USER - NEW CREATOR
@app.route('/user/Creator/newCreator', methods=['GET', 'POST'])
def newCreator():
    current_user = get_current_user()
    if request.method == 'POST':
        profile = request.files['profile']
        current_user.profile = profile.read()
        db.session.commit()
        return redirect('/user/registerAsCreator')
    return render_template('user/Creator/newCreator.html', csspage='/static/uploadSongs.css', username=current_user.name)

# CREATOR - REGISTER
@app.route('/user/registerAsCreator')
def register_as_creator():
    current_user = get_current_user()

    if current_user:
        current_user.is_creator = True
        db.session.commit()

    return redirect('/user/Creator/existCreator')


# CREATOR - NEW ALBUM
@app.route('/user/Album/newAlbum', methods=['GET', 'POST'])
def newAlbum():
    current_user = get_current_user()
    if request.method == 'POST':
        title = request.form.get('title')
        cover = request.files['cover']
        
        album = Album(title=title, cover=cover.read(), user_id=current_user.id)
        db.session.add(album)
        db.session.commit()
        return redirect('/user/Creator/existCreator')
    return render_template('/user/Album/newAlbum.html', csspage = '/static/uploadSongs.css', username=current_user.name)

# CREATOR UPLOAD SONGS
@app.route('/user/Song/uploadSongs', methods=['POST', 'GET'])
def uploadSongs():
    current_user = get_current_user()
    if request.method == 'POST':
        title = request.form.get('title')
        album_id = int(request.form.get('album'))
        genre = request.form.get('genre')
        lyrics = request.files['lyrics']
        file_data = request.files['songfile']

        song = Song(title=title, album_id=album_id, genre=genre, lyrics=lyrics.read(), file_data=file_data.read())
        db.session.add(song)
        db.session.commit()

        return redirect('/user/Song/uploadSongs')
    albums = Album.query.filter_by(user_id=current_user.id).all()
    return render_template('/user/Song/uploadSongs.html', csspage = '/static/uploadSongs.css', albums=albums, username=current_user.name)


# CREATOR - DASHBOARD
@app.route('/user/Creator/creatorDashboard')
def creatorDashboard():
    current_user = get_current_user()
    if current_user and current_user.is_creator:
        albums = Album.query.filter_by(user_id=current_user.id).all()
        return render_template('/user/Creator/creatorDashboard.html', csspage='/static/uploadSongs.css', albums=albums, username=current_user.name)
    else:
        return redirect('/user/')

@app.route('/get_lyrics/<int:song_id>')
def get_lyrics(song_id):
    song = Song.query.get(song_id)
    if song and song.lyrics:
        return song.lyrics.decode('utf-8')
    return "Lyrics not found", 404

@app.route('/user/blacklistUser/<int:user_id>', methods=['GET', 'POST'])
def blacklistUser(user_id):
    user = User.query.get(user_id)
    if user:
        if request.method == 'POST':
            user.blacklist = not user.blacklist
            db.session.commit()
        return redirect('/admin/dashboard')



# DELETE ALBUM
@app.route('/user/deleteAlbum/<int:album_id>')
def delete_album(album_id):
    current_user = get_current_user()
    if current_user and current_user.is_creator:
        album = Album.query.get(album_id)
        if album and album.user == current_user:
            db.session.delete(album)
            db.session.commit()

    return redirect(url_for('creatorDashboard'))



# USER - UPDATE ALBUM
@app.route('/user/Album/updateAlbum/<string:album_name>', methods=['GET', 'POST'])
def updateAlbum(album_name):
    current_user = get_current_user()
    album = Album.query.filter_by(title=album_name, user_id=current_user.id).first()
    if request.method == 'POST':
        new_title = request.form.get('title')
        new_cover = request.files['cover']
        if album:
            album.title = new_title
            if new_cover:
                album.cover = new_cover.read()
            db.session.commit()
            return redirect(url_for('creatorDashboard'))
    return render_template('user/Album/updateAlbum.html', album_name=album_name, csspage='/static/uploadSongs.css', username=current_user.name)




# DELETE SONG
@app.route('/user/deleteSong/<int:song_id>')
def delete_song(song_id):
    current_user = get_current_user()
    
    if current_user and current_user.is_creator:
        song = Song.query.get(song_id)
        
        if song and song.album.user == current_user:
            db.session.delete(song)
            db.session.commit()

    return redirect(url_for('creatorDashboard'))



# USER - UPDATE SONG
@app.route('/user/Album/updateSong/<string:song_name>', methods=['GET', 'POST'])
def updateSong(song_name):
    current_user = get_current_user()
    song = Song.query.filter_by(title=song_name).first()
    if request.method == 'POST':
        new_title = request.form.get('title')
        new_album_id = int(request.form.get('album'))
        new_genre = request.form.get('genre')
        new_lyrics = request.files['lyrics']
        new_file_data = request.files['songfile']
        if song:
            if new_title:
                song.title = new_title
            if new_album_id:
                song.album_id = new_album_id
            if new_genre:
                song.genre = new_genre
            if new_lyrics:
                song.lyrics = new_lyrics.read()
            if new_file_data:
                song.file_data = new_file_data.read()
            db.session.commit()
            return redirect(url_for('creatorDashboard'))
    albums = Album.query.filter_by(user_id=current_user.id).all()
    return render_template('user/Song/updateSong.html', song_name=song_name, albums=albums, csspage='/static/uploadSongs.css', username=current_user.name)


# USER - NEW PLAYLIST
@app.route('/user/Playlist/newPlaylist', methods=['POST', 'GET'])
def newPlaylist():
    current_user = get_current_user()
    if request.method == 'POST':
        title = request.form.get('title')

        playlist = Playlist(title=title, user_id=current_user.id)
        db.session.add(playlist)
        db.session.commit()

        return redirect('/user/userDashboard')
    return render_template('/user/PLaylist/newPlaylist.html', csspage='/static/uploadSongs.css', username=current_user.name)


# USER - ALBUM DISPLAY
@app.route('/user/Album/album')
def album():
    current_user = get_current_user()
    if current_user:
        albums = Album.query.all()
        album_name = request.args.get('album_name', '')
        album = Album.query.filter_by(title=album_name).first()
        songs = Song.query.filter_by(album_id=album.id).all()
        playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    return render_template('/user/Album/album.html', songs=songs, albums=albums, playlists=playlists, album_name=album.title, include_musicplayer=True, username=current_user.name)


# USER - PLAYLIST DISPLAY
@app.route('/user/Playlist/playlist')
def playlist():
    current_user = get_current_user()
    albums = Album.query.all()
    playlist_name = request.args.get('playlist_name', '')

    playlist = Playlist.query.filter_by(title=playlist_name, user_id=current_user.id).first()

    if playlist:
        songs = playlist.songs
    else:
        songs = []

    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    return render_template('/user/Playlist/playlist.html', songs=songs, albums=albums, playlists=playlists, playlist_name=playlist_name, include_musicplayer=True, username=current_user.name)

# USER - CREATOR DISPLAY
@app.route('/user/Creator/creator')
def viewCreator():
    current_user = get_current_user()
    users = User.query.all()
    user_name = request.args.get('user_name', '')
    user = User.query.filter_by(name=user_name).first()
    albums = Album.query.filter_by(user_id=user.id).all()
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    return render_template('/user/Creator/creator.html', albums=albums, playlists=playlists, user_name=user_name, include_musicplayer=True, username=current_user.name)

# USER - GENRE DISPLAY
@app.route('/user/Song/genre')
def genre():
    current_user = get_current_user()
    genre_name = request.args.get('genre_name', '')
    songs = Song.query.filter_by(genre=genre_name).all()
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    return render_template('/user/Song/genre.html', songs=songs, playlists=playlists, genre_name=genre_name, include_musicplayer=True, username=current_user.name)

# USER - ADD TO PLAYLIST
@app.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():
    playlist_id = request.form.get('playlist_id')
    song_id = request.form.get('song_id')
    playlist = Playlist.query.get(playlist_id)
    song = Song.query.get(song_id)

    if playlist and song:
        playlist.songs.append(song)
        db.session.commit()
    return redirect(url_for('userDashboard'))


# USER - DELETE PLAYLIST SONG
@app.route('/user/Playlist/deletePlaylistSong/<int:song_id>/<string:playlist_name>')
def deletePlaylistSong(song_id, playlist_name):
    playlist = Playlist.query.filter_by(title=playlist_name).first()
    song = Song.query.get(song_id)

    if playlist and song:
        playlist.songs.remove(song)
        db.session.commit()
    return redirect(url_for('playlist', playlist_name=playlist_name,))



# USER - DELETE PLAYLIST
@app.route('/user/deleteSong/<int:playlist_id>')
def deletePlaylist():
    if request.method == 'POST':
        current_user = get_current_user()
        title = request.form.get('title')

        playlist = Playlist(title=title, user_id=current_user.id)
        db.session.add(playlist)
        db.session.commit()

        return redirect('/user/userDashboard')


# USER - UPDATE PLAYLIST
@app.route('/user/Playlist/updatePlaylist/<string:playlist_name>', methods=['GET', 'POST'])
def updatePlaylist(playlist_name):
    current_user = get_current_user()
    if request.method == 'POST':
        new_title = request.form.get('title')
        playlist = Playlist.query.filter_by(title=playlist_name, user_id=current_user.id).first()
        if playlist:
            playlist.title = new_title
            db.session.commit()
            return redirect(url_for('playlist', playlist_name=new_title))
    return render_template('user/Playlist/updatePlaylist.html', playlist_name=playlist_name, csspage='/static/uploadSongs.css', username=current_user.name)
