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
2- Cluster-level permissions control your ability to use and modify a specific cluster. There are four permission levels for a cluster: No Permissions, Can Attach To, Can Restart, and Can Manage. The table lists the abilities for each permission:
<img width="870" height="587" alt="image" src="https://github.com/user-attachments/assets/3bf65f89-664d-404c-a0ec-88f7751e6cb1" />
</details>
<summary>Row filters and column masks</summary>
<details>
- (https://docs.databricks.com/aws/en/data-governance/unity-catalog/filters-and-masks)
- (https://docs.databricks.com/aws/en/data-governance/unity-catalog/filters-and-masks/manually-apply)
</details>

<summary>Optimize</summary>
<details>Delta OPTIMIZE – Complete Notes (Summary + Commands + Interview Points)
**OPTIMIZE** improves Delta table performance by reorganizing data files.
It mainly solves the small file problem by compacting many small files into fewer large files.
It uses bin-packing to create evenly sized files for efficient reads.
It does not change data, only improves storage layout and query performance.

Basic Commands
- Basic optimize:
- OPTIMIZE table_name;
- Optimize specific partitions:
- OPTIMIZE table_name WHERE date >= '2024-01-01';
- Optimize with ZORDER:
- OPTIMIZE table_name ZORDER BY (customer_id);
- Full table rewrite:
- OPTIMIZE table_name FULL;

### Key Features
Supports partition-level optimization using WHERE clause
ZORDER improves data skipping and query performance
FULL rewrites entire table data when needed
Idempotent operation (safe to run multiple times)
Works only with Delta tables

### When to Use
After heavy batch inserts
After streaming ingestion (many small files)
When query performance degrades
Periodic maintenance (daily/weekly)

### Important Notes (Interview Focus)
Small file problem is the primary reason for OPTIMIZE
ZORDER is clustering, not sorting
OPTIMIZE is an expensive operation, avoid overuse
Prefer partition filtering instead of full table optimize
Works well with Delta data skipping internally
Auto Optimize / Predictive Optimization can reduce manual effort

### VACUUM (Cleanup)
Removes old unused files after OPTIMIZE:
VACUUM table_name RETAIN 168 HOURS;

### File Size Control (Databricks Runtime)
Control output file size after OPTIMIZE using Spark config:
spark.conf.set("spark.databricks.delta.optimize.maxFileSize", 104857600)
Default: 1073741824 (1 GB)
Example: 104857600 (100 MB)

### File Size Tuning Notes
Smaller files → better parallelism
Larger files → better scan efficiency
Tune based on workload (streaming vs batch, query patterns)

### Simple Memory
OPTIMIZE = Compact files
ZORDER = Faster queries
VACUUM = Cleanup storage
File size tuning = Balance between parallelism and scan efficiency</details>

<summary>Manage data quality with pipeline expectations</summary>
<details>https://learn.microsoft.com/en-us/azure/databricks/ldp/expectations</details>

<summary>Autoloader partten</summary>
<details>https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/patterns</details>

<summary>Task Notification</summary>
<details>https://docs.databricks.com/aws/en/jobs/notifications</details>

<summary>Authorize access to Databricks resources</summary>
<details>https://docs.databricks.com/aws/en/dev-tools/auth/#authorization-methods</details>

<summary>secret access permissions</summary>
<details>The secret access permissions are as follows:
MANAGE - Allowed to change ACLs, and read and write to this secret scope.
WRITE - Allowed to read and write to this secret scope.
READ - Allowed to read this secret scope and list what secrets are available.
Each permission level is a subset of the previous level’s permissions (that is, a principal with WRITE permission for a given scope can perform all actions that require READ permission).</details>

<summary>Databricks to databricks and delta sharing </summary>
<details>There are mainly two ways to share data using Delta Sharing:
1- Databricks-to-Databricks sharing (D2D): it lets you share data from your Unity Catalog-enabled workspace with clients who also have access to a Unity Catalog-enabled Databricks workspace.
This approach uses the Delta Sharing server that is built into Databricks and provides support for notebook sharing, Unity Catalog data governance, auditing, and usage tracking for both providers and recipients.
2- Databricks open sharing protocol (D2O): It lets you share data that you manage in a Unity Catalog-enabled Databricks workspace with users on any computing platform.
This approach also uses the Delta Sharing server that is built into Databricks and is useful when you manage data using Unity Catalog and want to share it with users who don't use Databricks or don't have access to a Unity Catalog-enabled Databricks workspace.
So, D2D is optimized for seamless sharing within the Databricks ecosystem, whereas D2O extends interoperability to external platforms that support the open Delta Sharing protocol.</details>

<summary>Auto Optimize</summary>
<details>Auto Optimize is a functionality that allows Delta Lake to automatically compact small data files of Delta tables. This can be achieved during individual writes to the Delta table.
Auto optimize consists of 2 complementary operations:
- Optimized writes: with this feature enabled, Databricks attempts to write out 128 MB files for each table partition.
- Auto compaction: this will check after an individual write, if files can further be compacted. If yes, it runs an OPTIMIZE job with 128 MB file sizes (instead of the 1 GB file size used in the standard OPTIMIZE)</details>

<summary>Spark Declarative pipeline</summary>
<details>dlt.expect_all enforces all the specified data quality rules, writes both valid and invalid records to the target table, and captures metrics about any rule violations.
dlt.expect would not fully meet the requirements because it applies expectations individually but doesn’t automatically enforce all of them together as a group. Similarly, dlt.expect_or_drop removes individual invalid records, and dlt.expect_or_fail stops the pipeline on individual rule violations. You can group multiple expectations together and specify collective actions using the functions dlt.expect_all_or_drop, and dlt.expect_all_or_fail.
Note: Databricks has recenlty open-sourced this solution, integrating it into the Apache Spark ecosystem under the name Spark Declarative Pipelines (SDP).</details>

<summary>Static joins</summary>
<details>Stream-static joins take advantage of Delta Lake guarantee that the latest version of the static delta table is returned each time it is queried in a join operation with a data stream.</details>

<summary>databricks jobs list</summary>
<details>https://docs.databricks.com/aws/en/dev-tools/cli/reference/jobs-commands
The correct Databricks CLI command that allows a data engineer to list all runs of a job that started at or after a specific time is databricks jobs list-runs --job-id <job-id> --start-time-from <time-value>, as --start-time-from is the proper parameter used to filter job runs based on their start time in the Databricks CLI.
</details>

<summary>Files statistics in the Delta transaction log</summary>
<details>Overall explanation
In the Transaction log, Delta Lake captures statistics for each data file of the table. These statistics indicate per file:
Total number of records
Minimum value in each column of the first 32 columns of the table
Maximum value in each column of the first 32 columns of the table
Null value counts for in each column of the first 32 columns of the table
When a query with a selective filter is executed against the table, the query optimizer uses these statistics to generate the query result. it leverages them to identify data files that may contain records matching the conditional filter.
For the SELECT query in the question, The transaction log is scanned for min and max statistics for the price column.

</details>

<summary>Delta Lake automatically captures statistics</summary>
<details>Delta Lake automatically captures statistics in the transaction log for each added data file of the table. By default, Delta Lake collects the statistics on the first 32 columns of each table. Nested fields count when determining the first 32 columns



Example: 4 struct fields with 8 nested fields will total to the 32 columns.</details>

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

<summary></summary>
<details></details>

<summary></summary>
<details></details>




