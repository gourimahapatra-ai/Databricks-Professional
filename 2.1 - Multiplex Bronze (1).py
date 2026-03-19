# Databricks notebook source
# MAGIC %md-sandbox
# MAGIC
# MAGIC <div  style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://raw.githubusercontent.com/derar-alhussein/Databricks-Certified-Data-Engineer-Professional/main/Includes/images/bronze.png" width="60%">
# MAGIC </div>

# COMMAND ----------

# MAGIC %run ./Copy-Datasets

# COMMAND ----------

data_catalog = spark.sql("SELECT current_catalog()").collect()[0][0]
print (data_catalog)

# COMMAND ----------

display(dbutils.fs.ls("/Volumes/dbacademy/ops/labuser13431568_1773883293@vocareum_com/test/"))

# COMMAND ----------

files = dbutils.fs.ls(f"dbfs:/Volumes/dbacademy/ops/labuser13431568_1773883293@vocareum_com/test/")
display(files)

# COMMAND ----------

df_raw = spark.read.json(f"dbfs:/Volumes/dbacademy/ops/labuser13431568_1773883293@vocareum_com/test/")
display(df_raw)

# COMMAND ----------

from pyspark.sql import functions as F

def process_bronze():
  
    schema = "key BINARY, value BINARY, topic STRING, partition LONG, offset LONG, timestamp LONG"

    query = (spark.readStream
                        .format("cloudFiles")
                        .option("cloudFiles.format", "json")
                        .schema(schema)
                        .load(f"dbfs:/Volumes/dbacademy/ops/labuser13431568_1773883293@vocareum_com/test/")
                        .withColumn("timestamp", (F.col("timestamp")/1000).cast("timestamp"))  
                        .withColumn("year_month", F.date_format("timestamp", "yyyy-MM"))
                  .writeStream
                      .option("checkpointLocation", f"dbfs:/Volumes/dbacademy/ops/labuser13431568_1773883293@vocareum_com/test/")
                      .option("mergeSchema", True)
                      .partitionBy("topic", "year_month")
                      .trigger(availableNow=True)
                      .table("dbacademy.labuser13431568_1773883293.bronze"))
    
    query.awaitTermination()

# COMMAND ----------

process_bronze()

# COMMAND ----------

batch_df = spark.table("dbacademy.labuser13431568_1773883293.bronze")
display(batch_df)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM dbacademy.labuser13431568_1773883293.bronze

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT DISTINCT(topic)
# MAGIC FROM dbacademy.labuser13431568_1773883293.bronze

# COMMAND ----------

dbutils.fs.cp("s3://dalhussein-courses/DE-Pro/datasets/bookstore/v1//kafka-streaming/", "/Volumes/dbacademy/ops/labuser13431568_1773883293@vocareum_com/test/", True)

# COMMAND ----------

bookstore.load_new_data()

# COMMAND ----------

process_bronze()

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) FROM dbacademy.labuser13431568_1773883293.bronze