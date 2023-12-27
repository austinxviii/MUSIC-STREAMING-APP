from app import db

#USER CLASS
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    email = db.Column(db.String(255), nullable = False)
    is_creator = db.Column(db.Boolean, default=False)
    profile = db.Column(db.LargeBinary, nullable=True)
    albums = db.relationship('Album', backref='user')
    playlists = db.relationship('Playlist', backref='user')
    username = db.Column(db.String(255), nullable = False)
    password = db.Column(db.String(255), nullable = False)
    blacklist = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'User("{self.id}", "{self.name}", "{self.email}", "{self.username}", "{self.blacklist}")'


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


# ASSICIATION TABLE BETWEEN PLAYLIST AND SONG(MANY-TO-MANY)
song_playlist_association = db.Table('song_playlist_association',
    db.Column('song_id', db.Integer, db.ForeignKey('song.id')),
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'))
)


# PLAYLIST CLASS
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    songs = db.relationship('Song', secondary=song_playlist_association, backref='playlists')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'Playlist("{self.id}", "{self.title}", "{self.user_id}")'

    

# SONG CLASS
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))
    genre = db.Column(db.String(255), nullable=False)
    lyrics = db.Column(db.LargeBinary)
    file_data = db.Column(db.LargeBinary)

    def __repr__(self):
        return f'Song("{self.id}", "{self.title}", "{self.album_id}", "{self.genre}", "{self.lyrics}")'