<summary>Materialized View</summary>
<details> The most suitable object for this use case is a materialized view because it allows the data analyst to precompute and store business-level aggregations, such as total revenue, average order value, and units sold per category, so that downstream reports and dashboards can access the results quickly without recalculating them every time, unlike a temporary or standard view, which either exist only for the session or require repeated recomputation, and unlike a streaming table, which is designed for processing raw, real-time event streams rather than pre-aggregated summaries.
</details>

<summary> dbutils.secrets.get(SCOPE, KEY) </summary>
<details>Used to securely retrieve a secret where the first argument is the scope name (api_scope) and the second argument is the secret key (api_key).</details>

<summary> Clone a table on Databricks </summary>
<details> https://docs.databricks.com/aws/en/delta/clone

### - Clone types
- A deep clone is a clone that copies the source table data to the clone target in addition to the metadata of the existing table. Additionally, stream metadata is also cloned such that a stream that writes to the Delta table can be stopped on a source table and continued on the target of a clone from where it left off.
- A shallow clone is a clone that does not copy the data files to the clone target. The table metadata is equivalent to the source. These clones are cheaper to create.
- Use
 - Data archiving (CREATE OR REPLACE TABLE archive_table CLONE my_prod_table)
 - Use clone for ML model reproduction (CREATE TABLE model_dataset CLONE entire_dataset VERSION AS OF 15)
 - Use clone for short-term experiments on a production table
 - Use clone to override table properties
</details>

<summary>Write operations </summary>
<details>
ALTER TABLE users
ADD CONSTRAINT valid_age CHECK (age> 0);
Write operations failed because of the constraint violation. However, ACID guarantees on Delta Lake ensure that all transactions are atomic. That is, they will either succeed or fail completely. So in this case, none of these records have been inserted into the table, even the ones that don't violate the constraints.
</details>

<summary> Microbatch processing </summary>
<details> 
  
  ```python
  def upsert_data(microBatchDF, batch_id):
    microBatchDF.createOrReplaceTempView("sales_microbatch")
    
    sql_query = """
      MERGE INTO sales_silver a
      USING sales_microbatch b
      ON a.item_id=b.item_id AND a.item_timestamp=b.item_timestamp
      WHEN NOT MATCHED THEN INSERT *
    """  
    ### microBatchDF.sparkSession.sql(sql_query)
 ```
Usually, we use spark.sq() function to run SQL queries. However, in this particular case, the spark session can not be accessed from within the microbatch process. Instead, we can access the local spark session from the  microbatch dataframe.
For clusters with recent Databricks Runtime version above 10.5, the syntax to access the local spark session is:
### microBatchDF.sparkSession.sql(sql_query)

</details>

<summary> CDF = Change Data Feed </summary>
<details>
It is a feature in Delta Lake that lets you track changes (INSERT, UPDATE, DELETE) happening in a table. Instead of reading full table every time,
you can read only what changed
What changes are captured
CDF records:
✅ INSERT
✅ UPDATE
✅ DELETE
CDF will track all these changes : How to enable CDF :
### ALTER TABLE my_table SET TBLPROPERTIES (delta.enableChangeDataFeed = true);

```python
spark.read
        .option("readChangeFeed", "true")
        .option("startingVersion", 0)
        .table ("customers")
        .filter (col("_change_type").isin(["update_postimage"]))
    .write
        .mode("append")
        .table("customers_updates")
```
The entire history of updated records will be appended to the target table at each execution, which leads to duplicate entries.
Reading table’s changes, captured by CDF, using spark.read means that you are reading them as a static source. So, each time you run the query, all table’s changes (starting from the specified startingVersion) will be read.
The query in the question then appends the data to the target table at each execution since it’s using the ‘append’ writing mode.
### Output columns you get
 - CDF adds metadata columns:
  - _change_type → insert/update/delete
  - _commit_version → version of change
  - _commit_timestamp → when change happened
   
</details>

<summary>Table partitioning allows delete queries to leverage partition boundaries.</summary>
<details>Partitioning on datetime columns can be leveraged when removing data older than a certain age from the table. For example, you can decide to delete previous months data. In this case, file deletion will be cleanly along partition boundaries.
Similarly, data could be archived and backed up at partition boundaries to a cheaper storage tier. This drives a huge savings on cloud storage.</details>

<summary>Lakehouse Federation </summary>
<details>Lakehouse Federation is a feature in Databricks that enables users to query data in external databases directly, such as Oracle and SQL Server, without the need for data replication, ingestion, or movement. It provides a unified analytics layer on top of multiple data sources and allows for federated queries, where data from various platforms can be combined into a single logical view.</details>

<summary>Delta Lake’s default transaction log retention</summary>
<details>Delta Lake’s default transaction log retention period is 30 days, which determines how long historical data is kept available for time travel before being permanently deleted. To match this retention period for the deleted data files, we need to alter the table to set the table property 'delta.deletedFileRetentionDuration', as follows:
ALTER TABLE orders SET TBLPROPERTIES ('delta.deletedFileRetentionDuration’ = 'interval 30 days")</details>

<summary></summary>
<details></details>

<summary></summary>
<details></details>

<summary></summary>
<details></details>

<summary></summary>
<details></details>

<summary></summary>
<details></details>
