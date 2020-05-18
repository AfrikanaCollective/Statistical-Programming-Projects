from pyspark import SparkContext,SparkConf

conf = SparkConf().setMaster("local").setAppName("Customer_Expense")
sc = SparkContext(conf=conf)

expenses = sc.textFile("file:///SparkCourse/customer-orders.csv")

def expenseattributes(line):
    customer_expense = line.split(",")
    return customer_expense[0],float(customer_expense[2])

costs = expenses.map(expenseattributes).reduceByKey(lambda x,y:x+y).map(lambda x: (x[1],x[0])).sortByKey()
results = costs.collect()
for result in results:
    print("User: {}, Costs {:.2f}".format(result[1],result[0]))