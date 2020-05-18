import re
from pyspark import SparkConf, SparkContext

def normalizeWords(text):
    return re.compile(r'\W+', re.UNICODE).split(text.lower())

conf = SparkConf().setMaster("local").setAppName("WordCount")
sc = SparkContext(conf = conf)

input = sc.textFile("file:///SparkCourse/book.txt")
words = input.flatMap(normalizeWords)

##wordCounts = words.countByValue()

wordCounts = words.map(lambda x:(x,1)).reduceByKey(lambda x,y:x+y)
wordCountsSorted = wordCounts.map(lambda x:(x[1],x[0])).sortByKey()
results = wordCountsSorted.collect()

for result in results:
    word = result[1].encode("ascii","ignore")
    if (word):
        print(word.decode() +":\t\t" + str(result[0]))
