# coding=utf-8

import sys
import numpy as np
from pyspark import SparkContext, SparkConf

conf = SparkConf()
sc = SparkContext(conf=conf)

# https://blog.cambridgespark.com/nowadays-recommender-systems-are-used-to-personalize-your-experience-on-the-web-telling-you-what-120f39b89c3c
# https://towardsdatascience.com/various-implementations-of-collaborative-filtering-100385c6dfe0

# aws s3 cp s3://afrikana-collective/1M_Movie_Rating.py ./
# aws s3 cp s3://afrikana-collective/movie-reviews/movies.dat ./
# spark-submit --executor-memory 1g 1M_Movie_Rating.py 260 1493
#
# Item-Item Collaborative Filtering: “Users who liked this movie also liked …”
# User-Item Collaborative Filtering: “Users who are similar to you also liked …”
#


def loadMovieNames():
    movieNames = {}
    with open("movies.dat") as f:
        for line in f:
            fields = line.split("::")
            movieNames[int(fields[0])] = fields[1].decode('ascii','ignore')
    return movieNames


print("\nLoading movie names...\n")
nameDict = loadMovieNames()

movieRatingsRdd = sc.textFile("s3n://afrikana-collective/movie-reviews/ratings.dat")


# Remove duplicate ratings (hint: one half of the n*n matrix)
# Key1,Key2 can be either user or item, based on filtering technique
def isDuplicate(pairedUserRatings):
    ratingsPair = pairedUserRatings[1]
    (key1,rating1) = ratingsPair[0]
    (key2,rating2) = ratingsPair[1]
    return key1 < key2


# Item-based filtering
# (User, Movie => Rating)
movieRatings = movieRatingsRdd\
                .map(lambda line:line.split("::"))\
                .map(lambda line:(int(line[0]),(int(line[1]),float(line[2]))))

# Combine every movie rated by same user
# ratings consists of userID => ((movieID, rating), (movieID, rating))
movieRatingsPartitioned = movieRatings.partitionBy(100)
ratings = movieRatings.join(movieRatingsPartitioned)
uniqueItemRatings = ratings.filter(isDuplicate)

# User-based filtering
# Record: (Movie, User => Rating)
userRatings = movieRatingsRdd\
                .map(lambda line:line.split("::"))\
                .map(lambda line:(int(line[1]),(int(line[0]),float(line[2]))))

# Combine every user rating by same movie
# Ratings consists of movieID => ((userID, rating), (userID, rating))
ratings = userRatings.join(userRatings)
uniqueUserRatings = ratings.filter(isDuplicate)


# Memory based filtering
#
# Item-based filtering: convert ratings from userID => ((movieID, rating), (movieID, rating))
# to userID => ((movieID1, movieID2), (rating1, rating2))
#
# User-based filtering: convert ratings from movieID => ((userID, rating), (userID, rating))
# to movieID => ((userID1, userID2), (rating1, rating2))
#
def pairwiseMovieRatings(pairedRating):
    ratingsPair = pairedRating[1]
    (key1, rating1) = ratingsPair[0]
    (key2, rating2) = ratingsPair[1]
    return (key1,key2),(rating1,rating2)


moviePairs = uniqueItemRatings.map(pairwiseMovieRatings).partitionBy(100)
userPairs = uniqueUserRatings.map(pairwiseMovieRatings).partitionBy(100)

userPairingRatings = userPairs.groupByKey()  # Convert to (user1, user2) => (rating1, rating2),(rating1, rating2)...
moviePairingRatings = moviePairs.groupByKey()  # Convert to (movie1, movie2) => (rating1, rating2),(rating1, rating2)...


def flattenPairings(pairsRatings):
    ratings1, ratings2 = map(list, zip(*pairsRatings))
    return ratings1,ratings2


movieRatingSimilarities = moviePairingRatings.mapValues(flattenPairings)
userRatingSimilarities = userPairingRatings.mapValues(flattenPairings)


# Input as (movie1, movie2) => [rating1.1, rating1.2, ...],[rating2.1, rating2.2, ...]
# Input as (user1, user2) => [rating1.1, rating1.2, ...],[rating2.1, rating2.2, ...]
def getScores(moviePairRatingsTuple):
    numPairs = len(moviePairRatingsTuple[0])
    score = np.dot(moviePairRatingsTuple[0], moviePairRatingsTuple[1]) / (
            np.linalg.norm(moviePairRatingsTuple[0]) * np.linalg.norm(moviePairRatingsTuple[1]))

    return numPairs, score


# Compute similarities in scoring
movieRatingSimilaritieScores = movieRatingSimilarities.mapValues(getScores).persist()
userRatingSimilaritieScores = userRatingSimilarities.mapValues(getScores).persist()

klScoreThreshold = 0.975
coOccurenceMoviesThreshold = 1000 # Similar movie ratings have at least 50 co-occurrences
coOccurenceUserRatingThreshold = 10 #Similar users ratings have at least 10 co-occurrences

# Filter for movies with similarities that are "good" as defined by
# our quality thresholds above

if len(sys.argv) > 1:
    movieID = int(sys.argv[1])
    userID = int(sys.argv[2])

    filteredResultsByMovie = movieRatingSimilaritieScores.filter(lambda result:
                                                               (result[0][0] == movieID or result[0][1] == movieID) and
                                                               result[1][0] > coOccurenceMoviesThreshold and
                                                               result[1][1] > klScoreThreshold)

    filteredResultsByUser = userRatingSimilaritieScores.filter(lambda result:
                                                             (result[0][0] == userID or result[0][1] == userID) and
                                                             result[1][0] > coOccurenceUserRatingThreshold and
                                                             result[1][1] > klScoreThreshold)


    resultsMovies = filteredResultsByMovie\
        .map(lambda result:(result[1][1],(result[0][1] if result[0][1]!=movieID else result[0][0],result[1][0])))\
        .sortByKey(ascending=False)\
        .take(5)

    resultsUsers = filteredResultsByUser \
        .map(lambda result: (result[1][1], (result[0][1] if result[0][1] != userID else result[0][0], result[1][0]))) \
        .sortByKey(ascending=False) \
        .take(5)
    
    print("\n\nTop 5 similar movies for {}\n".format(nameDict[movieID]))
    for result in resultsMovies:
        print("{}\t\tscore: {:.4f}\t\tvotes: {}".format(nameDict[result[1][0]],float(result[0]),result[1][1]))

    print("\n\nTop 5 similar users for user {}\n".format(userID))
    for result in resultsUsers:
        print("{}\t\tscore: {:.4f}\t\tvotes: {}".format(result[1][0],float(result[0]),result[1][1]))
