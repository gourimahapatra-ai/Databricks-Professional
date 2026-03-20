### 1. window("order_timestamp", "15 minutes")
is used in structured streaming or batch aggregations to group data into time-based windows.
- Simple way to remember : “Group data by time chunks
What it means : 
It creates a time interval structure like:
[window.start, window.end)
Example:
- 10:00 to 10:15
- 10:15 to 10:30
### Variations :
- window("order_timestamp", "15 minutes", "5 minutes")
  - 15 minutes → window size
  - 5 minutes → sliding interval
- This creates overlapping windows (sliding windows)
```python
from pyspark.sql.functions import window

df.groupBy(
    window("order_timestamp", "15 minutes")
).count()
```
👉 So this creates fixed 15-minute buck

### 2. trigger(processingTime="15 minutes")
Run the streaming query every 15 minutes
```python
query = df.writeStream \
    .format("delta") \
    .outputMode("append") \
    .trigger(processingTime="15 minutes") \
    .start()
```
>[!IMPORTANT]
> - Compare with other triggers
>  - Default (no trigger) : Runs as fast as possible
>  - processingTime="15 minutes" : Fixed interval (controlled, predictable)
>  - trigger(once=True) : Runs one batch and stops
>  - trigger(availableNow=True) : Processes all available data and stops (used in batch-like streaming)

### 3. outputMode("append") means:
👉 Only write NEW rows (final results) to the output
👉 Already written data is never updated
👉 Simple understanding
👉 Data comes → processed → only new results are added
👉 Old results → remain unchanged
```python
df.writeStream \
  .outputMode("append") \
  .format("delta") \
  .start()
```
### How it behaves
1. Input (1, 100) - > output (1, 100)
2. Input (2, 200) - > output (2, 200)
3. Input (2, 200) - > output (2, 200)
4. Final (1, 100,2, 200,2, 200)

- No future updates expected
- Typically used with:
- event-time + watermark
- or simple streaming inserts
```python
from pyspark.sql.functions import window

df.withWatermark("order_timestamp", "10 minutes") \
  .groupBy(window("order_timestamp", "15 minutes")) \
  .count() \
  .writeStream \
  .outputMode("append") \
  .start()
```
### Why this order matters
- withWatermark() → tells Spark how long to wait for late data
- groupBy(window()) → performs aggregation
- Spark needs watermark info before aggregation starts

### What this pipeline does
Watermark (10 minutes)
→ Late data allowed up to 10 mins 
Window (15 minutes)
→ Groups data into 15-min buckets
Append mode
→ Outputs only final results after watermark passes
> [!IMPORTANT]
> - Important behavior (very interview-focused)
> - Spark waits until window is complete + watermark passed
> - Then only → result is appended once
> - No updates later
### trigger-interval
```python
(spark.readStream
        .table("orders")
    .writeStream
        .option("checkpointLocation", checkpointPath)
        .table("Output_Table")
)
```
##### By default, if you don’t provide any trigger interval, the data will be processed every half second. This is equivalent to trigger(processingTime=”500ms") 

### 4. LDP pipeline
```python
@dlt.table
@dlt.expect_or_drop("positive_price", "price > 0")
def silver_products():
    return spark.readStream.table("bronze_products")
 
@dlt.table
@dlt.expect_or_drop("invalid_price", "price <= 0")
def quarantine_products():
    return spark.readStream.table("bronze_products")
```
#### 5. This LDP pipeline uses a common pattern for quarantining records by creating a second table that stores the invalid records.
The silver_products table uses **@dlt.expect_or_drop("positive_price", "price > 0")** , which means that only records meeting the condition price > 0 are kept, while any records with zero or negative prices are dropped. As a result, the silver_products table contains only valid product records where prices are positive, ensuring that downstream processes receive clean and business-rule-compliant data.
On the other hand, the quarantine_products table is defined with **@dlt.expect_or_drop("invalid_price", "price <= 0")**, meaning only records with zero or negative prices satisfy this expectation and are retained. This effectively routes all invalid price records into the quarantine table for further inspection or correction.
The original bronze_products table remains unchanged, and no records are deleted from it.
* Databricks has recenlty open-sourced this solution, integrating it into the Apache Spark ecosystem under the name Spark Declarative Pipelines (SDP).

### 6. Correctly orders the Lakeflow Declarative pipeline permissions from least privilege to most privilege
CAN VIEW → CAN RUN → CAN MANAGE
In permission hierarchies, least privilege to most privilege means starting with the minimal access and ending with full control.
**CAN VIEW**: allows only viewing pipeline details, Spark UI, and driver logs.
**CAN RUN**: allows executing the pipeline but not modifying it.
**CAN MANAGE**: allows full control, including executing, editing, deleting, and managing permissions.
The same concept applies to **job permissions**.

### 7. For production Structured Streaming jobs, which of the following retry policies is recommended to use?
**Unlimited Retries, with 1 Maximum Concurrent Run**
[Link](https://docs.databricks.com/aws/en/structured-streaming/production#configure-structured-streaming-jobs-to-restart-streaming-queries-on-failure)
In order to restart streaming queries on failure, it’s recommended to configure Structured Streaming jobs with the following job configuration:
Retries: Set to Unlimited.
Maximum concurrent runs: Set to 1. There must be only one instance of each query concurrently active.
Cluster: Set this always to use a new job cluster and use the latest Spark version (or at least version 2.1). Queries started in Spark 2.1 and above are recoverable after query and Spark version upgrades.
Notifications: Set this if you want email notification on failures.
Schedule: Do not set a schedule.
Timeout: Do not set a timeout. Streaming queries run for an indefinitely long time.

### 8. Develop a job with Declarative Automation Bundles [Link](https://docs.databricks.com/aws/en/dev-tools/bundles/jobs-tutorial)
Step 1: Set up authentication
 - databricks auth login --host <workspace-url>
 - databricks auth token --host <workspace-url>
 - databricks auth token -p <profile-name>
 - databricks auth token --host <workspace-url> -p <profile-name>
Step 2: Initialize the bundle : Initialize a bundle using the default Python bundle project template.
 - databricks bundle init
Step 3: Explore the bundle : To view the files that the template generated, switch to the root directory of your newly created bundle. Files of particular interest include the following:
  - **databricks.yml:** This file specifies the bundle's programmatic name, includes references to the bundle's files, defines catalog and schema variables, and specifies settings for target workspaces.
  - **resources/sample_job.job.yml:** This file specifies the job's settings, including a default notebook task. For information about job settings, see job.
  - **src/:** This folder contains the job's source files.
  - **src/sample_notebook.ipynb:** This notebook reads a sample table.
  - **tests/: **This folder contains sample unit tests.
  - **README.md:** This file contains additional information about getting started and using this bundle template.

Step 4: Validate the bundle configuration : Now check whether the bundle configuration is valid
 - databricks bundle validate
Step 5: Deploy the bundle to the remote workspace
 - databricks bundle deploy --target dev or - databricks bundle deploy --t dev
Step 6: Run the deployed job
 - databricks bundle run --target dev sample_job
Step 7: Run tests : Finally, use pytest to run tests locally:
 - uv run pytest
Step 8: Clean up
 - databricks bundle destroy --target dev
 
### 9. Develop pipelines with Declarative Automation Bundles [Link](https://docs.databricks.com/aws/en/dev-tools/bundles/pipelines-tutorial)
Step-by-step with commands

Install and configure CLI : databricks configure
Initialize a bundle project : databricks bundle init
Move into project directory : cd <your-bundle-folder>

 - Validate bundle configuration : databricks bundle validate
 - Deploy pipeline to workspace : databricks bundle deploy
 - Run the deployed pipeline : databricks bundle run
 - Check pipeline or job status : databricks bundle run --refresh-all
 - View logs and debug : via CLI or workspace UI
 - Make changes in code or configuration and redeploy : databricks bundle deploy
 - Destroy resources when done : databricks bundle destroy
 - Simple understanding: Init → Validate → Deploy → Run → Monitor → Destroy

### Update table schema [Link](https://docs.databricks.com/aws/en/delta/update-schema#add-columns-with-automatic-schema-update)
Add columns with automatic schema update (summary with commands)
- Databricks supports automatic schema evolution to add new columns.
- Enable schema evolution during write using the mergeSchema option.
- df.write.format("delta").option("mergeSchema", "true").mode("append").save("/path")
**Works for both batch and streaming writes.**
- df.writeStream.format("delta").option("mergeSchema", "true").start("/path")
- New columns in incoming data are automatically added to the target table.
- New columns are appended at the end of the schema.
- Existing records get NULL values for newly added columns.
- If schema evolution is not enabled, write will fail due to schema mismatch.
- Schema evolution can also be used with MERGE operations.
```SQL
MERGE INTO target t
USING source s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```
```python
spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", checkpointPath)
        .load(source_path)
    .writeStream
        .option("checkpointLocation", checkpointPath)
        .___________  option("mergeSchema", True)
        .start("target_table")
```        
- You can enable it globally (not recommended for strict control).
- spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
- Best practice is to enable schema evolution only when required per operation.
- Simple memory: New columns come → enable mergeSchema → table auto-updates
