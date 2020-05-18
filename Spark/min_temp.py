from pyspark import SparkContext,SparkConf

conf = SparkConf().setMaster("local").setAppName("temp_calc")
sc = SparkContext(conf=conf)

lines = sc.textFile("file:///SparKCourse/1800.csv")

def parseline(line):
    fields = line.split(",")
    station = fields[0]
    entrytype = fields[2]
    temp=float(fields[3])*0.1 * (9.0/5.0) + 32.0
    return station,entrytype,temp


parsedLines = lines.map(parseline)
minTemps = parsedLines.filter(lambda x: "TMIN" in x[1])

stationTemps = minTemps.map(lambda x:(x[0],x[2]))

minimumTemp = stationTemps.reduceByKey(lambda x,y: min(x,y))
results = minimumTemp.collect()

for result in results:
    print(result[0] + "\t{:.2f}F".format(result[1]))