# Databricks-Professional

https://github.com/derar-alhussein/Databricks-Certified-Data-Engineer-Professional.git

Step To Create Data

Step 1.

#Create volume
spark.sql("""
CREATE VOLUME IF NOT EXISTS dbacademy.labuser13431568_1773894869.data
""")

Step 2

spark.conf.set("fs.s3a.endpoint", "s3.eu-west-3.amazonaws.com")
spark.conf.set("fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider")
dbutils.fs.cp("s3://dalhussein-courses/DE-Pro/datasets/bookstore/v1//books-updates-streaming/", "/Volumes/dbacademy/labuser13431568_1773894869/data/books-updates-streaming/", True)

#List
display(dbutils.fs.ls("/Volumes/dbacademy/labuser13431568_1773894869/data/books-updates-streaming/"))

#Add one more file
spark.conf.set("fs.s3a.endpoint", "s3.eu-west-3.amazonaws.com")
spark.conf.set("fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider")
dbutils.fs.cp("s3://dalhussein-courses/DE-Pro/datasets/bookstore/v1//kafka-streaming/", "/Volumes/dbacademy/labuser13431568_1773894869/data/books-updates-streaming/", True)


# Databricks-Professional

#https://github.com/derar-alhussein/Databricks-Certified-Data-Engineer-Professional.git

#Step To Create Data

#Create two folder data and  books-updates-streaming

#Step 1.

#Create volume
spark.sql("""
CREATE VOLUME IF NOT EXISTS dbacademy.labuser13431568_1773894869.data
""")

#Step 2

spark.conf.set("fs.s3a.endpoint", "s3.eu-west-3.amazonaws.com")
spark.conf.set("fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider")
dbutils.fs.cp("s3://dalhussein-courses/DE-Pro/datasets/bookstore/v1//books-updates-streaming/", "/Volumes/dbacademy/labuser13431568_1773894869/data/books-updates-streaming/", True)

#List
display(dbutils.fs.ls("/Volumes/dbacademy/labuser13431568_1773894869/data/books-updates-streaming/"))

#Add one more file
spark.conf.set("fs.s3a.endpoint", "s3.eu-west-3.amazonaws.com")
spark.conf.set("fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider")
dbutils.fs.cp("s3://dalhussein-courses/DE-Pro/datasets/bookstore/v1//kafka-streaming/", "/Volumes/dbacademy/labuser13431568_1773894869/data/books-updates-streaming/", True)


data_catalog = spark.sql("SELECT current_catalog()").collect()[0][0]
print (data_catalog)

files = dbutils.fs.ls(f"/Volumes/dbacademy/labuser13431568_1773894869/data/books-updates-streaming/")
display(files)

df_raw_01 = spark.read.json(f"/Volumes/dbacademy/labuser13431568_1773894869/data/books-updates-streaming/01.json")
display(df_raw_01)

df_raw = spark.read.json(f"/Volumes/dbacademy/labuser13431568_1773894869/data/books-updates-streaming/")
display(df_raw)

df_raw.count()


from pyspark.sql import functions as F

def process_bronze():
  
    schema = "key BINARY, value BINARY, topic STRING, partition LONG, offset LONG, timestamp LONG"

    query = (spark.readStream
                        .format("cloudFiles")
                        .option("cloudFiles.format", "json")
                        .schema(schema)
                        .load(f"/Volumes/dbacademy/labuser13431568_1773894869/data/books-updates-streaming/")
                        .withColumn("timestamp", (F.col("timestamp")/1000).cast("timestamp"))  
                        .withColumn("year_month", F.date_format("timestamp", "yyyy-MM"))
                  .writeStream
                      .option("checkpointLocation", f"/Volumes/dbacademy/labuser13431568_1773894869/data/books-updates-streaming/checkpointLocation")
                      .option("mergeSchema", True)
                      .partitionBy("topic", "year_month")
                      .trigger(availableNow=True)
                      .table("dbacademy.labuser13431568_1773894869.bronze_booksSelf"))
    
    query.awaitTermination()

process_bronze()

batch_df = spark.table("dbacademy.labuser13431568_1773894869.bronze_booksSelf")
display(batch_df)

%sql
SELECT * FROM dbacademy.labuser13431568_1773894869.bronze_booksSelf

%sql
SELECT DISTINCT(topic)
FROM dbacademy.labuser13431568_1773894869.bronze_booksSelf

spark.conf.set("fs.s3a.endpoint", "s3.eu-west-3.amazonaws.com")
spark.conf.set("fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider")
dbutils.fs.cp("s3://dalhussein-courses/DE-Pro/datasets/bookstore/v1//kafka-streaming/", "/Volumes/dbacademy/labuser13431568_1773894869/data/books-updates-streaming/", True)

process_bronze()

%sql
--SELECT COUNT(*) FROM dbacademy.labuser13431568_1773894869.bronze_booksSelf
SELECT * FROM dbacademy.labuser13431568_1773894869.bronze_booksSelf
