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

- Databricks records change data for UPDATE, DELETE, and MERGE operations in the _change_data folder under the table directory.
- The files in the _change_data folder follow the retention policy of the table. Therefore, if you run the VACUUM command, change data feed data is also deleted.
</details>

<summary>Table partitioning allows delete queries to leverage partition boundaries.</summary>
<details>Partitioning on datetime columns can be leveraged when removing data older than a certain age from the table. For example, you can decide to delete previous months data. In this case, file deletion will be cleanly along partition boundaries.
Similarly, data could be archived and backed up at partition boundaries to a cheaper storage tier. This drives a huge savings on cloud storage.</details>

<summary>Lakehouse Federation </summary>
<details>Lakehouse Federation is a feature in Databricks that enables users to query data in external databases directly, such as Oracle and SQL Server, without the need for data replication, ingestion, or movement. It provides a unified analytics layer on top of multiple data sources and allows for federated queries, where data from various platforms can be combined into a single logical view.</details>

<summary>Delta Lake’s default transaction log retention</summary>
<details>Delta Lake’s default transaction log retention period is 30 days, which determines how long historical data is kept available for time travel before being permanently deleted. To match this retention period for the deleted data files, we need to alter the table to set the table property 'delta.deletedFileRetentionDuration', as follows:
ALTER TABLE orders SET TBLPROPERTIES ('delta.deletedFileRetentionDuration’ = 'interval 30 days")</details>

<summary>liquid clustering</summary>
<details>In this scenario, using liquid clustering on the combination of user_id and event_date is the best choice to avoid expensive scans. This technique incrementally optimizes data layout based on both columns, efficiently supporting filters on these columns and avoiding costly table scans.
Partitioning only on event_date helps queries filtering by date but doesn’t optimize filtering by user_id, leading to potential full scans within partitions. Z-order indexing on user_id optimizes queries filtering on user_id but ignores event_date filtering, resulting in inefficient scans when filtering by date. Lastly, partitioning on user_id + Z-order on event_date supports filtering on both columns but can create many small partitions (if users are numerous), causing management and performance issues.

- Automatic Liquid Clustering in Delta Lake is enabled using CLUSTER BY AUTO. This allows Delta to automatically manage clustering based on query patterns and data distribution, without manually specifying columns.
- The other options are incorrect because CLUSTER BY (id, updated, value) manually specifies clustering columns, so it does not enable automatic clustering. CLUSTER BY NONE explicitly disables liquid clustering, and CLUSTER BY ALL is not valid Delta Lake syntax.
```SQL
CREATE OR REPLACE TABLE orders(id int, updated date, value double)
CLUSTER BY AUTO;
```
</details>

<summary>ISO/UTC Time Zone</summary>
<details>In Databricks jobs, all time-based references are based on a timestamp in the UTC timezone, including: is_weekday, iso_weekday, iso_datetime, and iso_date.
This ensures consistency across regions, clusters, and users regardless of their local time zones.
[Link](https://docs.databricks.com/aws/en/jobs/dynamic-value-references)
</details>

<summary>Data Sharing, Delta Sharing</summary>
<details>[https://www.databricks.com/product/delta-sharing]
Databricks-to-Databricks Delta Sharing enables sharing data securely with any Databricks client, regardless of account or cloud host, as long as that the client has access to a workspace enabled for Unity Catalog.
</details>

<summary>Improve table read performance with history sharing</summary>
<details>Databricks-to-Databricks table shares can improve performance by enabling history sharing using the WITH HISTORY clause. Sharing history improves performance by leveraging temporary security credentials from your cloud storage, scoped-down to the root directory of the provider's shared Delta table, resulting in performance that is comparable to direct access to source tables.
- It leverages temporary security credentials from the cloud storage, scoped-down to the root directory of the provider's shared Delta table.</details>

<summary>Partition</summary>
<details>Table partitioning helps improve security. You can separate sensitive and nonsensitive data into different partitions and apply different security controls to the sensitive data.
* Personally Identifiable Information or PII represents any information that allows identifying individuals by either direct or indirect means, such as the name and the email of the user.</details>

<summary>CONSTRAINT valid_id EXPECT (id IS NOT NULL) _____________</summary>
<details>By default, records that violate the constraint will still be written to the target table and reported as invalid in the pipeline metrics. Therefore, the constraint can simply be defined as CONSTRAINT valid_id EXPECT (id IS NOT NULL) without any ON VIOLATION clause.
Note: Databricks has recenlty open-sourced this solution, integrating it into the Apache Spark ecosystem under the name Spark Declarative Pipelines (SDP).</details>

<summary>data quality validation in a Lakeflow Declarative Pipeline (LDP)</summary>
<details>dlt.expect_or_warn is not a supported expectation function in Lakeflow Declarative Pipelines (LDP).
- LDP supports the following expectation functions:
- dlt.expect: it writes invalid rows to the target (warning semantics)
- dlt.expect_or_drop: drops invalid rows before writing to the target.
- dlt.expect_or_fail: fails the update if violation occurs
Note: Databricks has recenlty open-sourced this solution, integrating it into the Apache Spark ecosystem under the name Spark Declarative Pipelines (SDP).</details>

<summary>Predictive Optimization</summary>
<details>Predictive Optimization in Databricks Unity Catalog automatically optimizes managed tables in Unity Catalog by:
- Running background maintenance tasks like VACUUM, OPTIMIZE, and ANALYZE to reduce fragmentation and improve performance.
- Collecting table statistics during writes, which helps the query optimizer make better decisions and improve query speed.</details>

<summary>Job Run</summary>
<details>
 - The Jobs API allows you to create, edit, and delete jobs.
 - POST /api/2.2/jobs/run-now : Run a job and return the run_id of the triggered run.
 - GET /api/2.0/permissions/jobs/{job_id} : Gets the permissions of a job. Jobs can inherit permissions from their root object.
 - PUT /api/2.0/permissions/jobs/{job_id} : Set job permissions
 Base URL

https://<databricks-instance>/api/2.1/jobs/

🔹 Common Jobs APIs

List all jobs
GET /api/2.1/jobs/list
👉 Returns all jobs in the workspace

Get job details
GET /api/2.1/jobs/get?job_id=<job_id>
👉 Fetch details of a specific job

Create a job
POST /api/2.1/jobs/create
👉 Creates a new job

Update a job
POST /api/2.1/jobs/update
👉 Updates an existing job

Delete a job
POST /api/2.1/jobs/delete
👉 Deletes a job

Run a job (trigger run)
POST /api/2.1/jobs/run-now
👉 Triggers an immediate run of a job

Submit one-time run
POST /api/2.1/jobs/runs/submit
👉 Runs a job without creating it permanently

List job runs
GET /api/2.1/jobs/runs/list
👉 Lists all runs of jobs

Get run details
GET /api/2.1/jobs/runs/get?run_id=<run_id>
👉 Get details of a specific run

Cancel run
POST /api/2.1/jobs/runs/cancel
👉 Stops a running job

Get run output
GET /api/2.1/jobs/runs/get-output?run_id=<run_id>
👉 Fetch output/logs of a run

Repair job run
POST /api/2.1/jobs/runs/repair
👉 Retry failed tasks in a run

🔹 Simple understanding

👉 Jobs API = Create → Run → Monitor → Manage jobs programmatically
 https://docs.databricks.com/api/workspace/jobs/runnow</details>

<summary>Hash</summary>
<details>
The reason both hashes have the same length comes from how cryptographic hash functions are designed. SHA-256 always produces a 256-bit output, no matter how long or short the input is. This is a fundamental property of cryptographic hash functions—they map inputs of arbitrary size to a fixed-length output.
Whether you hash "spark123" (8 characters) or "ApacheSpark111" (14 characters), SHA-256 will still generate 256 bits, typically represented as 64 hexadecimal characters. When represented as a hexadecimal string (which is standard for storing hashes), a 256-bit hash is always 64 characters long.
```SQL
SELECT sha2('spark123', 256);
92f55da1cdca0fd9811daa0bc97455c9e9e2b16d29e4e142c56e5924a1446175

SELECT sha2('ApacheSpark111', 256);
5385cb3eb8907791fe9efad61f847bb9af6145a6db5689f7687bf7f1c3e25086
```
As you can see, both the hash of "spark123" and the hash of "ApacheSpark111" have the same length, which is 64 hexadecimal characters. So, for the data engineer in this question, the column constraint should be set to accommodate 64-character.
</details>

<summary>Merge</summary>
<details>Merge operation can not be performed if multiple source rows matched and attempted to modify the same target row in the table. The result may be ambiguous as it is unclear which source row should be used to update or delete the matching target row.
For such an issue, you need to preprocess the source table to eliminate the possibility of multiple matches.</details>

<summary>Cluster Permission</summary>
<details>You can configure two types of cluster permissions:
1- The ‘Allow cluster creation’ entitlement controls your ability to create clusters.
2- Cluster-level permissions control your ability to use and modify a specific cluster. There are four permission levels for a cluster: No Permissions, Can Attach To, Can Restart, and Can Manage. The table lists the abilities for each permission:</details>
<img width="870" height="587" alt="image" src="https://github.com/user-attachments/assets/3bf65f89-664d-404c-a0ec-88f7751e6cb1" />

<summary>Row filters and column masks</summary>
<details>
- (https://docs.databricks.com/aws/en/data-governance/unity-catalog/filters-and-masks)
- (https://docs.databricks.com/aws/en/data-governance/unity-catalog/filters-and-masks/manually-apply)
</details>
