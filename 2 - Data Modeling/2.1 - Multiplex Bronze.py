# Databricks notebook source
# MAGIC %md-sandbox
# MAGIC
# MAGIC <div  style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://raw.githubusercontent.com/derar-alhussein/Databricks-Certified-Data-Engineer-Professional/main/Includes/images/bronze.png" width="60%">
# MAGIC </div>

# COMMAND ----------

data_catalog = spark.sql("SELECT current_catalog()").collect()[0][0]
print (data_catalog)

# COMMAND ----------

labuser = "labuser13431568_1773907580"
spark.sql(f"DROP TABLE IF EXISTS dbacademy.{labuser}.bronze_booksSelf")

# COMMAND ----------

spark.sql(f"CREATE VOLUME IF NOT EXISTS dbacademy.{labuser}.data")

# COMMAND ----------

dbutils.fs.rm(f"dbfs:/Volumes/dbacademy/{labuser}/data/books-updates-streaming", True)
dbutils.fs.mkdirs(f"dbfs:/Volumes/dbacademy/{labuser}/data/books-updates-streaming")

# COMMAND ----------

dbutils.fs.mkdirs(f"dbfs:/Volumes/dbacademy/{labuser}/data")
dbutils.fs.mkdirs(f"dbfs:/Volumes/dbacademy/{labuser}/data/books-updates-streaming")
dbutils.fs.mkdirs(f"dbfs:/Volumes/dbacademy/{labuser}/data/checkpoint")

# COMMAND ----------

files = dbutils.fs.ls(f"dbfs:/Volumes/dbacademy/{labuser}/data/")
display(files)

# COMMAND ----------

display(dbutils.fs.ls(f"/Volumes/dbacademy/{labuser}/data/books-updates-streaming/"))

# COMMAND ----------

#display(dbutils.fs.ls("s3://dalhussein-courses/DE-Pro/datasets/bookstore/v1/books-updates-streaming/"))

# COMMAND ----------

spark.conf.set("fs.s3a.endpoint", "s3.eu-west-3.amazonaws.com")
spark.conf.set("fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider")
dbutils.fs.cp("s3://dalhussein-courses/DE-Pro/datasets/bookstore/v1/books-updates-streaming//", f"/Volumes/dbacademy/{labuser}/data/books-updates-streaming/", True)

# COMMAND ----------

display(dbutils.fs.ls(f"/Volumes/dbacademy/{labuser}/data/books-updates-streaming/"))

# COMMAND ----------

from pyspark.sql import functions as F

def process_bronze():
  
    schema = "key BINARY, value BINARY, topic STRING, partition LONG, offset LONG, timestamp LONG"

    query = (spark.readStream
                    .format("cloudFiles")
                    .option("cloudFiles.format", "json")
                    .schema(schema)
                    .load(f"/Volumes/dbacademy/{labuser}/data/books-updates-streaming/")
                    .withColumn("timestamp", (F.col("timestamp")/1000).cast("timestamp"))  
                    .withColumn("year_month", F.date_format("timestamp", "yyyy-MM"))
              .writeStream
                  .option("checkpointLocation", f"dbfs:/Volumes/dbacademy/{labuser}/data/checkpoint")
                  .option("mergeSchema", True)
                  .partitionBy("topic", "year_month")
                  .trigger(availableNow=True)
                  .table(f"dbacademy.{labuser}.bronzeBooksSelf"))
    
    query.awaitTermination()

# COMMAND ----------

process_bronze()

# COMMAND ----------

batch_df = spark.table(f"dbacademy.{labuser}.bronzeBooksSelf")
display(batch_df)

# COMMAND ----------

display(spark.sql(f"SELECT * FROM dbacademy.{labuser}.bronzeBooksSelf"))

# COMMAND ----------

display(spark.sql(f"SELECT DISTINCT(topic) FROM dbacademy.{labuser}.bronzeBooksSelf"))

# COMMAND ----------

dbutils.fs.cp("s3://dalhussein-courses/DE-Pro/datasets/bookstore/v1/kafka-streaming/", f"/Volumes/dbacademy/{labuser}/data/books-updates-streaming", True)

# COMMAND ----------

process_bronze()

# COMMAND ----------

spark.sql(f"DROP TABLE IF EXISTS dbacademy.{labuser}.bronzeBooksSelf")

# COMMAND ----------

display(spark.sql(f"SELECT * FROM dbacademy.{labuser}.bronzeBooksSelf"))
