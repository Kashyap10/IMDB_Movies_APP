class Urls:
    """
    This class is contains list of urls
    """
    Registration =  "/register"
    HomePage = "/imdb"
    MovieName = "/imdb/moviename/<string:name>"
    MovieScore = "/imdb/score/<string:score>"
    MovieDirector = "/imdb/director/<string:director>"
    MovieGenre = "/imdb/genre/<string:genre>"