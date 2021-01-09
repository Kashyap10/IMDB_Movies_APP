from tabledetails import IMDB
from config import Config
import jwt
import datetime

class Helper():
    @staticmethod
    def encode_auth_token(userdata):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=10),
                'iat': datetime.datetime.utcnow(),
                'uid': userdata['uid'],
                'pwd':userdata['pwd'],
                'role': userdata['role']
            }
            return jwt.encode(
                payload,
                Config.SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, Config.SECRET_KEY)
            return payload['role']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    @staticmethod
    def get_results_list(movies):
        """
        This method will return movie list
        :param movies: movies data
        :return:
        """
        resultlist = [
                    {
                        IMDB.name: movie.name,
                        IMDB.imdb_score: movie.imdb_score,
                        IMDB.director: movie.director,
                        IMDB.popularity: movie.popularity,
                        IMDB.genre: movie.genre
                    } for movie in movies]
        return resultlist