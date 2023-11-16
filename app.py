from flask import Flask, render_template, flash, request, redirect, send_file, make_response, session, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import io

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///songs.sqlite"
app.config["SECRET_KEY"] = '8af126e22aacd3584bb381f2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]='filesystem'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
Session(app)
app.app_context().push()

#USER CLASS
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    email = db.Column(db.String(255), nullable = False)
    is_creator = db.Column(db.Boolean, default=False)
    albums = db.relationship('Album', backref='user')
    username = db.Column(db.String(255), nullable = False)
    password = db.Column(db.String(255), nullable = False)

    def __repr__(self):
        return f'User("{self.id}", "{self.name}", "{self.email}", "{self.username}")'


# ADMIN CLASS
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(255), nullable = False)
    password = db.Column(db.String(255), nullable = False)

    def __repr__(self):
        return f'Admin("{self.id}", "{self.username}")'


# ALBUM CLASS
class Album(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255), nullable = False)
    songs = db.relationship('Song', backref='album', cascade='all, delete-orphan')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cover = db.Column(db.LargeBinary)

    def __repr__(self):
        return f'Album("{self.id}", "{self.title}", "{self.songs}", "{self.cover}")'

    

#SONG CLASS
class Song(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255), nullable = False) 
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))
    genre = db.Column(db.String(255), nullable = False)
    lyrics = db.Column(db.LargeBinary)
    file_data = db.Column(db.LargeBinary)

    def __repr__(self):
        return f'Song("{self.id}", "{self.title}", "{self.album_id}", "{self.genre}", "{self.lyrics}")'



db.create_all()


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
    return render_template('/admin/dashboard.html', title="Admin Dashboard")


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

# ADMIN GET ALL USERS
@app.route('/admin/all-users', methods=["POST","GET"])
def adminGetAllUser():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if request.method== "POST":
        search=request.form.get('search')
        users=User.query.filter(User.username.like('%'+search+'%')).all()
        return render_template('admin/all-users.html',users=users)
    else:
        users=User.query.all()
        return render_template('admin/all-users.html',users=users)


# ADMIN CHANGE PASSWORD
@app.route('/admin/admin-change-password',methods=["POST","GET"])
def adminChangePassword():
    admin=Admin.query.get(1)
    if request.method == 'POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if username == "" or password=="":
            flash('Please enter all the fields','danger')
            return redirect('/admin/admin-change-password')
        else:
            Admin().query.filter_by(username=username).update(dict(password=bcrypt.generate_password_hash(password,10)))
            db.session.commit()
            flash('Admin Password updated successfully','success')
            return redirect('/admin/admin-change-password')
    else:
        return render_template('admin/admin-change-password.html',title='Admin Change Password',admin=admin)


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
        return redirect('/user/')

# USER CHANGE PASSWORD
@app.route('/user/change-password', methods=["POST", "GET"])
def userChangePassword():
    if not session.get('user_id'):
        return redirect('/user/')
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        if email == '' or username == '' or password == '':
            flash("Enter all the fields", 'danger')
            return redirect('/user/change-password')
        else:
            users = User.query.filter_by(email=email).first
            if users:
                hash_password = bcrypt.generate_password_hash(password, 10)
                User.query.filter_by(email=email).update(dict(password = hash_password))
                db.session.commit()
                flash("Password changed successfully", 'success')
                return redirect('/user/change-password')
            else:
                flash("Invalid Email", 'danger')
                return redirect('/user/change-password')
    else:
        return render_template('/user/change-password.html', title="Change Password")



# USER DASHBOARD
@app.route('/user/userDashboard')
def userDashboard():
    songs = Song.query.all()
    albums = Album.query.all()
    return render_template('/user/userDashboard.html', songs=songs, albums=albums, include_musicplayer=True)

# GET COVER
@app.route('/album_cover/<int:album_id>')
def get_album_cover(album_id):
    album = Album.query.get(album_id)
    if album and album.cover:
        return send_file(io.BytesIO(album.cover), mimetype='image/jpg')
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
@app.route('/user/existCreator')
def creator():
    # Assuming you have a function to get the current user based on your authentication logic
    current_user = get_current_user()

    if current_user and current_user.is_creator:
        return render_template('/user/existCreator.html', csspage='/static/existcreat.css')
    else:
        return redirect('/user/newCreator')

# USER - NEW CREATOR
@app.route('/user/newCreator')
def newCreator():
    return render_template('user/newCreator.html', csspage='/static/existcreat.css')


@app.route('/user/registerAsCreator')
def register_as_creator():
    # Assuming you have a way to identify the current user (replace get_current_user with your logic)
    current_user = get_current_user()

    if current_user:
        # Update is_creator to True and save to the database
        current_user.is_creator = True
        db.session.commit()

    return redirect('/user/existCreator')


# CREATOR - NEW ALBUM
@app.route('/user/newAlbum', methods=['GET', 'POST'])
def newAlbum():
    current_user = get_current_user()
    if request.method == 'POST':
        title = request.form.get('title')
        cover = request.files['cover']
        
        album = Album(title=title, cover=cover.read(), user_id=current_user.id)
        db.session.add(album)
        db.session.commit()
        return redirect('/user/existCreator')
    return render_template('/user/newAlbum.html', csspage = '/static/uploadSongs.css')

# CREATOR UPLOAD SONGS
@app.route('/user/uploadSongs', methods=['POST', 'GET'])
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

        return redirect('/user/uploadSongs')
    albums = Album.query.filter_by(user_id=current_user.id).all()
    return render_template('/user/uploadSongs.html', csspage = '/static/uploadSongs.css', albums=albums)


# CREATOR - DASHBOARD
@app.route('/user/creatorDashboard')
def creatorDashboard():
    # Assuming you have a way to identify the current user (replace get_current_user with your logic)
    current_user = get_current_user()
    if current_user and current_user.is_creator:
        # Query albums associated with the current user
        albums = Album.query.filter_by(user_id=current_user.id).all()
        return render_template('/user/creatorDashboard.html', csspage='/static/uploadSongs.css', albums=albums)
    else:
        # Redirect to login or handle the case where the user is not a creator
        return redirect('/user/')  # Redirect to the login page or handle accordingly

@app.route('/get_lyrics/<int:song_id>')
def get_lyrics(song_id):
    song = Song.query.get(song_id)
    if song and song.lyrics:
        # Assuming the lyrics are stored as text in the database
        return song.lyrics.decode('utf-8')
    return "Lyrics not found", 404


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


if __name__ == "__main__":
    app.run(debug = True)