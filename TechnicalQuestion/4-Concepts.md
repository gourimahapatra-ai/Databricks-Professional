<summary>
Streaming code analysis
</summary>
<details>
  # 📘 Delta Lake Upsert (MERGE) Patterns in Databricks / PySpark

## 1. Basic Insert Only (When Not Matched)

```python
def upsert_data(microBatchDF, batch_id):
    microBatchDF.createOrReplaceTempView("sales_microbatch")

    sql_query = """
        MERGE INTO sales_silver a
        USING sales_microbatch b
        ON a.item_id = b.item_id
           AND a.item_timestamp = b.item_timestamp
        WHEN NOT MATCHED THEN INSERT *
    """

    spark.sql(sql_query)
```

## 2. Insert + Update (Most Common)

```python
def upsert_data(microBatchDF, batch_id):
    microBatchDF.createOrReplaceTempView("sales_microbatch")

    sql_query = """
        MERGE INTO sales_silver a
        USING sales_microbatch b
        ON a.item_id = b.item_id

        WHEN MATCHED THEN
          UPDATE SET *

        WHEN NOT MATCHED THEN
          INSERT *
    """

    spark.sql(sql_query)
```

## 3. Conditional Update

```python
sql_query = """
    MERGE INTO sales_silver a
    USING sales_microbatch b
    ON a.item_id = b.item_id

    WHEN MATCHED AND a.item_timestamp < b.item_timestamp THEN
      UPDATE SET *

    WHEN NOT MATCHED THEN
      INSERT *
"""
```

## 4. Selective Column Update

```python
sql_query = """
    MERGE INTO sales_silver a
    USING sales_microbatch b
    ON a.item_id = b.item_id

    WHEN MATCHED THEN
      UPDATE SET 
        a.price = b.price,
        a.quantity = b.quantity

    WHEN NOT MATCHED THEN
      INSERT (item_id, price, quantity)
      VALUES (b.item_id, b.price, b.quantity)
"""
```

## 5. CDC (Insert + Update + Delete)

```python
sql_query = """
    MERGE INTO sales_silver a
    USING sales_microbatch b
    ON a.item_id = b.item_id

    WHEN MATCHED AND b.operation = 'DELETE' THEN
      DELETE

    WHEN MATCHED AND b.operation = 'UPDATE' THEN
      UPDATE SET *

    WHEN NOT MATCHED AND b.operation = 'INSERT' THEN
      INSERT *
"""
```

## 6. DataFrame API (DeltaTable)

```python
from delta.tables import DeltaTable

def upsert_data(microBatchDF, batch_id):
    delta_table = DeltaTable.forName(spark, "sales_silver")

    delta_table.alias("a") \
        .merge(
            microBatchDF.alias("b"),
            "a.item_id = b.item_id"
        ) \
        .whenMatchedUpdateAll() \
        .whenNotMatchedInsertAll() \
        .execute()
```

## 7. Partition-Based Merge

```python
sql_query = """
    MERGE INTO sales_silver a
    USING sales_microbatch b
    ON a.item_id = b.item_id
       AND a.partition_date = b.partition_date

    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
"""
```

## 8. Deduplicate Before Merge

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

def upsert_data(microBatchDF, batch_id):
    window_spec = Window.partitionBy("item_id").orderBy("item_timestamp")

    dedup_df = microBatchDF.withColumn("rn", row_number().over(window_spec)) \
                           .filter("rn = 1") \
                           .drop("rn")

    dedup_df.createOrReplaceTempView("sales_microbatch")

    spark.sql("""
        MERGE INTO sales_silver a
        USING sales_microbatch b
        ON a.item_id = b.item_id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)
```

## 9. Streaming (foreachBatch)

```python
query = df.writeStream \
    .foreachBatch(upsert_data) \
    .outputMode("update") \
    .start()
```

# 🚀 Best Practices

- Avoid `INSERT *` in production → define columns explicitly  
- Deduplicate data before MERGE  
- Use partition filters for large tables  
- Optimize tables using `OPTIMIZE`  
- Use ZORDER on frequently joined columns  


# 🧠 When to Use What

| Scenario | Pattern |
|----------|--------|
| Only new data | Insert only |
| Slowly changing data | Insert + Update |
| CDC pipelines | Insert + Update + Delete |
| Large datasets | Partition-based merge |
| Streaming ingestion | foreachBatch + MERGE |


# ✅ Summary

MERGE is the core operation for:
- Upserts
- CDC handling
- Streaming data pipelines
- Data warehouse modeling (Silver layer)

</details>

<summary>Key SQL Metrics Displayed</summary>
<details>
# 📘 Spark UI SQL Metrics – Summary

## 🧠 Overview

In **Spark UI → SQL Tab → Query Details**, Spark displays execution-level metrics that help analyze performance, data movement, and resource usage for a query.

## ✅ Key SQL Metrics

### 1. Duration
- Total execution time of the query

### 2. Number of Output Rows
- Rows produced by each operator
- Helps detect data explosion or filtering impact

### 3. Input Size / Output Size
- Data read and written during execution
- Useful for identifying heavy I/O operations

### 4. Shuffle Read / Shuffle Write
- Data exchanged between executors
- Critical for joins and aggregations

### 5. Spill (Memory / Disk)
- Data spilled due to insufficient memory
- Indicates memory pressure

### 6. Execution Time per Operator
- Time taken by each step in the query plan
- Helps identify slow transformations

### 7. Number of Tasks
- Total parallel tasks executed
- Reflects level of parallelism

### 8. Scan Metrics
- Files read
- Bytes read
- Partitions scanned

## 🎯 Important Metrics (Exam Focus)

- Duration  
- Number of Output Rows  
- Shuffle Read / Write  
- Spill (Memory/Disk)  
- Input / Output Size  

## 🧩 Quick Understanding

Spark SQL metrics mainly focus on:
- ⏱ Time  
- 📊 Data volume  
- 🔁 Shuffle operations  
- 💾 Memory usage  

## ✅ One-Line Answer

Spark UI SQL query details page displays metrics such as duration, number of output rows, input/output size, shuffle read/write, spill, and execution time per operator.

</details>

<summary></summary>
<details># Databricks `ALTER TABLE ... SET TBLPROPERTIES` – Complete Guide

## 🔷 1. Set Multiple Properties

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES (
  'delta.appendOnly' = true,
  'delta.autoOptimize.optimizeWrite' = true,
  'delta.autoOptimize.autoCompact' = true
);
```

**Use case:** Combine governance + performance settings

## 🔷 2. Remove Properties

```sql
ALTER TABLE bronze_raw 
UNSET TBLPROPERTIES ('delta.appendOnly');
```

**Note:** Removes property completely

## 🔷 3. Set Property During Table Creation

```sql
CREATE TABLE bronze_raw (
  id INT,
  name STRING
)
USING DELTA
TBLPROPERTIES ('delta.appendOnly' = true);
```

**Best practice:** Define rules from the beginning


## 🔷 4. Change Property Value

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES ('delta.appendOnly' = false);
```

**Use case:** Temporarily allow updates


## 🔷 5. Performance Optimization Properties

### Optimize Write

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = true);
```

* Improves file sizes during write

### Auto Compaction

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES ('delta.autoOptimize.autoCompact' = true);
```

* Merges small files automatically


## 🔷 6. Data Retention

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES ('delta.deletedFileRetentionDuration' = '7 days');
```

* Controls how long deleted files are kept

Used with:

```sql
VACUUM bronze_raw;
```

---

## 🔷 7. Enable Change Data Feed (CDC)

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES ('delta.enableChangeDataFeed' = true);
```

**Use case:**

* Track inserts, updates, deletes
* Incremental pipelines

---

## 🔷 8. Column Mapping (Advanced)

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES ('delta.columnMapping.mode' = 'name');
```

* Enables safe schema evolution
* Required for column rename

## 🔷 9. Log Retention

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES ('delta.logRetentionDuration' = '30 days');
```

* Controls transaction log retention

## 🔷 10. Governance Property Comparison

### Append Only

```sql
'delta.appendOnly' = true
```

* Blocks UPDATE, DELETE, MERGE

### Read-only

* Managed via permissions (not TBLPROPERTIES)

## 🔷 11. Compatibility Property

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES ('delta.minReaderVersion' = '2');
```

* Ensures compatibility with advanced features

## 🔷 12. View Properties

```sql
SHOW TBLPROPERTIES bronze_raw;
```

## 🔷 13. Real-world Bronze Table Setup

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES (
  'delta.appendOnly' = true,
  'delta.autoOptimize.optimizeWrite' = true,
  'delta.autoOptimize.autoCompact' = true,
  'delta.enableChangeDataFeed' = true
);
```

**Benefits:**

* Immutability
* Better performance
* CDC tracking

## 🔷 14. Categories of Properties

| Category         | Examples                     |
| ---------------- | ---------------------------- |
| Governance       | delta.appendOnly             |
| Performance      | optimizeWrite, autoCompact   |
| Retention        | deletedFileRetentionDuration |
| CDC              | enableChangeDataFeed         |
| Schema Evolution | columnMapping                |

## 🔷 15. Common Mistake

❌ Wrong:

```sql
delta.appendOnly = true
```

✅ Correct:

```sql
'delta.appendOnly' = true
```

## 🔷 Final Summary

* `SET TBLPROPERTIES` controls Delta table behavior
* Used for governance, performance, retention, and streaming
* `appendOnly` ensures immutability
* Combine multiple properties for production-ready tables
* 
</details>

<summary></summary>
<details></details>

<summary></summary>
<details></details>






