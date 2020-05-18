from pyspark import SparkConf,SparkContext


conf = SparkConf().setMaster("local").setAppName("FakeSNA")
sc = SparkContext(conf=conf)

lines =sc.textFile("file:///SparkCourse/fakefriends.csv")
rdd = lines.map(lambda x:[int(y) for y in (x.split(",")[2:4])])

sumByAge = rdd.mapValues(lambda x:(x,1)).reduceByKey(lambda x,y: (x[0]+y[0], x[1]+y[1]))
averageByAge = sumByAge.mapValues(lambda x: x[0]/x[1])
results = averageByAge.collect()
for i in results:
    print(i)