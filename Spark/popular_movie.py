from pyspark.sql import Row, functions, SparkSession
import numpy as np
import collections

spark = SparkSession.builder.config("spark.sql.warehouse.dir", "file:///C:/temp").appName("PopularMovies").getOrCreate()


def loadMovieNames():
    movieNames = {}
    with open("ml-100k/u.item") as file:
        for line in file:
            fields = line.split("|")
            movieNames[int(fields[0])] = fields[1]
    return movieNames


# Load movie ID => name as dictionary
nameDict = loadMovieNames()
movieRatings = spark.sparkContext.textFile("file:///Statistical Programming Projects/Spark/ml-100k/u.data")

# RDD version
# movieClicks = movieRatings.map(lambda x:(int(x.split()[1]),1)).reduceByKey(lambda x,y:x+y)#.map(lambda x:(x[1],
# x[0])).sortByKey()

# SQL version
movieClicks = movieRatings.map(lambda x: Row(movieID=int(x.split()[1])))
movieDataset = spark.createDataFrame(movieClicks)

# SQL type approach
topMovieIDs = movieDataset.groupBy("movieID").count().orderBy("count", ascending=False).cache()

topMovieIDs.show()  # print table of top 10

done = [print("{}: {}".format(nameDict[result[0]], result[1])) for result in topMovieIDs.take(10)]

spark.stop()  # Stop session
