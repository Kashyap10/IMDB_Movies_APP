from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask,request,jsonify
from flask_restful import  Resource
from helper import Helper
from config import *
from tabledetails import IMDB
from sqlalchemy.dialects.postgresql import ARRAY
from flask_restful import Api
from urls import Urls

# Initiate flask app with and setup SQLAlchemy databse uri
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create db object  of SQLAlchemy
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class ImdbModel(db.Model):
    __tablename__ = 'imdb'
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    imdb_score = db.Column(db.Float())
    director = db.Column(db.String())
    name = db.Column(db.String())
    popularity = db.Column(db.Float())
    genre = db.Column(ARRAY(db.String))

    def __init__(self, name,imdb_score,director,popularity,genre):
        self.name = name
        self.imdb_score = imdb_score
        self.director = director
        self.popularity = popularity
        self.genre = genre

    def __repr__(self):
        return f"<Name {self.name}>"

class Register(Resource):
    """
    Registration class for user and admin
    """
    def post(self):
        '''
        This api takes body param like this
        {
            "uid":"abc@xyz.com",
            "pwd":"abc123",
            "role" : 1 or o ( 1 = admin or 0 = user)
        }
        :return: It will return jwt token user need to pass this token in header like auth : eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MDc4NjUxODYsImlhdCI6MTYwNzg2NTE4MSwidWlkIjoiYWJjQHh5ei5jb20iLCJyb2xlIjoxfQ.w8AmQHxeMD6lGk4_v21OJu1CVhZX6NdDpwqSb0317RE
        '''
        data = request.get_json()
        if not data:
            data = {"response": "ERROR"}
            return jsonify(data)
        else:
            token = Helper.encode_auth_token(data)
            return jsonify({"token": str(token)})

class Imdb(Resource):
    def get(self, name=None, score=None, director=None,genre=None):

        '''
        :param name:  if user wants to search movies by name then user need to pass movie name like /imdb/moviename/sample_movie_name
        :param score: if user wants to search movies by it's imdb score grater than particular value then user need to pass movie imdb_score like /imdb/score/sample_score
        :param director: if user wants to search movies by director name then user need to pass director name like /imdb/director/sample_director_name
        :param genre: if user wants to search movie by genre then user need to pass genre nname like /imdb/genre/samaple_genre_name
        :return:  user will get movie details in json format
        '''

        if name:
            movies = ImdbModel.query.filter(ImdbModel.name == name).all()

            if movies:
                results = Helper.get_results_list(movies)
                return jsonify({"count": len(results), "movies": results})
            else:
                return {"response": "no movie found for movie name equal to {0}".format(name)}
        elif score:
            movies = ImdbModel.query.filter(ImdbModel.imdb_score >= score).all()

            if movies:
                results = Helper.get_results_list(movies)
                return jsonify({"count": len(results), "movies": results})
            else:
                return {"response": "no movie found for greater then this {0} score".format(score)}

        elif director:
            movies = ImdbModel.query.filter(ImdbModel.director == director).all()

            if movies:
                results =Helper.get_results_list(movies)
                return jsonify({"count": len(results), "movies": results})
            else:
                return {"response": "no movie found for {0} as a director".format(director)}
        elif genre:
            movies = ImdbModel.query.filter(ImdbModel.genre.any(genre)).all()

            if movies:
                results = Helper.get_results_list(movies)
                return jsonify({"count": len(results), "movies": results})
            else:
                return {"response": "no movie found for {0} as a genre".format(genre)}
        else:
            movies = ImdbModel.query.all()

            if movies:
                results = Helper.get_results_list(movies)
                return jsonify({"count": len(results), "movies": results})
            else:
                return jsonify({"response": "no movies found"})

    def post(self):
        '''
        By using this Api user can add new movie details
        For this user need to pass jwt token in header's auth param if user's role is 1(admin) then user can add movie other wise operation will not be allowed
        :return:
        '''
        role = Helper.decode_auth_token(request.headers.get('auth'))
        if role == 1:
            data = request.get_json()
            if not data:
                data = {"response": "No data available in payload"}
                return jsonify(data)
            else:
                new_movie = ImdbModel(name=data[IMDB.name], imdb_score=data[IMDB.imdb_score], director=data[IMDB.director],popularity= data[IMDB.popularity],genre= data[IMDB.genre])
                db.session.add(new_movie)
                db.session.commit()
                return {"message": f"New movie {new_movie.name} has been created successfully."}
        else:
            return {"response": "User is not authorized to access the resource"}

    def put(self, name):
        '''
        BY using this api user can update existing movie details
        For this user need to pass jwt token in header's auth param if user's role is 1(admin) then user can add movie other wise operation will not be allowed
        :param name: user needs pass movie name which he want's to change
        :return:
        '''
        role = Helper.decode_auth_token(request.headers.get('auth'))
        if role == 1:
            data = request.get_json()
            if not data:
                data = {"response": "No data available in payload"}
                return jsonify(data)
            else:
                moviename = ''
                movies = ImdbModel.query.filter(ImdbModel.name == name).all()
                for movie in movies:
                    moviename = movie.name
                    movie.name = data[IMDB.name]
                    movie.imdb_score = data[IMDB.imdb_score]
                    movie.director = data[IMDB.director]
                    movie.popularity = data[IMDB.popularity]
                    movie.genre = data[IMDB.genre]
                    db.session.add(movie)
                    db.session.commit()
                return {"message": f"Movie {moviename} is successfully updated"}
        else:
            return {"response": "User is not authorized to access the resource"}

    def delete(self, name=None,director=None):
        '''
        By using this api user can delete existing movie details
        For this user need to pass jwt token in header's auth param if user's role is 1(admin) then user can add movie other wise operation will not be allowed
        :param name: user needs pass movie name which he want's to change
        :return:
        '''
        role = Helper.decode_auth_token(request.headers.get('auth'))
        if role == 1:
            if name:
                moviename = ''
                movies = ImdbModel.query.filter(ImdbModel.name == name).all()
                for movie in movies:
                    moviename = movie.name
                    db.session.delete(movie)
                    db.session.commit()
                return {"message": f"Movie {moviename} successfully deleted."}
            elif director:
                directorname = ''
                movies = ImdbModel.query.filter(ImdbModel.director == director).all()
                for movie in movies:
                    directorname = movie.director
                    db.session.delete(movie)
                    db.session.commit()
                return {"message": f"Movie {directorname} successfully deleted."}
            else:
                pass
        else:
            return {"response": "User is not authorized to access the resource"}

api = Api(app)
api.add_resource(Register, Urls.Registration)
api.add_resource(Imdb, Urls.HomePage, endpoint="imdb")
api.add_resource(Imdb, Urls.MovieName, endpoint="name")
api.add_resource(Imdb, Urls.MovieScore, endpoint="score")
api.add_resource(Imdb, Urls.MovieDirector, endpoint="director")
api.add_resource(Imdb, Urls.MovieGenre, endpoint="genre")

if __name__ == '__main__':
    app.run()