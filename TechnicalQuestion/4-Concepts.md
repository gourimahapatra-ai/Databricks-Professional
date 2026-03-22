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

<summary>Table Properties</summary>
<details>
# Databricks Delta Table Properties – Complete Guide
## Core Properties

```sql
'delta.appendOnly' = true,
'delta.autoOptimize.optimizeWrite' = true,
'delta.autoOptimize.autoCompact' = true
```

# 🔷 1. delta.appendOnly = true

### 👉 Meaning
- Only INSERT allowed , ❌ No UPDATE , ❌ No DELETE, ❌ No MERGE  

### ✅ Use Cases
- Bronze / Raw tables  
- Audit logs  
- Streaming ingestion  

### 💡 Think
“Do not modify existing data, only add new data”

# 2. delta.autoOptimize.optimizeWrite = true

### 👉 Meaning
- Writes data in optimised file sizes automatically

### 🚨 Problem it solves
- Too many small files during write

### ✅ Use Cases
- Batch ingestion  
- Streaming ingestion  

### 💡 Think
“Write data properly the first time”

# 🔷 3. delta.autoOptimize.autoCompact = true

### 👉 Meaning
- Automatically merges small files after write

### 🚨 Problem it solves
- Small files → slow queries  

### ✅ Use Cases
- Frequent small data loads  
- Streaming pipelines  

### 💡 Think
“Clean up small files after writing”

# 🔷 Quick Difference

| Property        | When it works   | Purpose            |
|----------------|---------------|--------------------|
| appendOnly     | Before change | Data safety        |
| optimizeWrite  | During write  | Better file size   |
| autoCompact    | After write   | Merge small files  |

# 🔷 Other Important Variations

## Set Multiple Properties

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES (
  'delta.appendOnly' = true,
  'delta.autoOptimize.optimizeWrite' = true,
  'delta.autoOptimize.autoCompact' = true
);
```

## Remove Property

```sql
ALTER TABLE bronze_raw 
UNSET TBLPROPERTIES ('delta.appendOnly');
```
## Set During Table Creation

```sql
CREATE TABLE bronze_raw (
  id INT,
  name STRING
)
USING DELTA
TBLPROPERTIES ('delta.appendOnly' = true);
```

## Change Property

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES ('delta.appendOnly' = false);
```

# Data Retention

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES ('delta.deletedFileRetentionDuration' = '7 days');
```

```sql
VACUUM bronze_raw;
```
# Change Data Feed (CDC)

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES ('delta.enableChangeDataFeed' = true);
```

# Column Mapping

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES ('delta.columnMapping.mode' = 'name');
```

# Log Retention

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES ('delta.logRetentionDuration' = '30 days');
```

# View Properties

```sql
SHOW TBLPROPERTIES bronze_raw;
```
# Real-world Bronze Setup

```sql
ALTER TABLE bronze_raw 
SET TBLPROPERTIES (
  'delta.appendOnly' = true,
  'delta.autoOptimize.optimizeWrite' = true,
  'delta.autoOptimize.autoCompact' = true,
  'delta.enableChangeDataFeed' = true
);
```

# Categories

| Category          | Examples                          |
|------------------|----------------------------------|
| Governance       | delta.appendOnly                 |
| Performance      | optimizeWrite, autoCompact       |
| Retention        | deletedFileRetentionDuration     |
| CDC              | enableChangeDataFeed             |
| Schema Evolution | columnMapping                    |

# Common Mistake

❌ Wrong:
```sql
delta.appendOnly = true
```

✅ Correct:
```sql
'delta.appendOnly' = true
```

# Memory Trick

- appendOnly → Protect data  
- optimizeWrite → Write better  
- autoCompact → Fix later  

# Final Summary

- Controls Delta table behavior  
- Used for governance, performance, retention  
- Combine properties for production-ready tables  

</details>

<summary>Query Profile</summary>
<details># Databricks Query Profile – Concise Summary

## 🔷 What is Query Profile?

- A **visual tool** to analyze query execution  
- Helps identify **performance bottlenecks**  
- Shows **operators, metrics, and execution flow** :contentReference[oaicite:0]{index=0}  

---

## 🔷 Why it is used

- Find **slow parts of a query**  
- Analyze **time, rows processed, memory usage**  
- Detect issues like:
  - Full table scans  
  - Exploding joins :contentReference[oaicite:1]{index=1}  

---

## 🔷 How to Access

1. Go to **Query History**
2. Click a query
3. Click **“See Query Profile”**

👉 Requires:
- Query owner OR  
- `CAN MONITOR` permission :contentReference[oaicite:2]{index=2}  

---

## 🔷 Query Summary (Top Section)

- Query status (Queued, Running, Finished, Failed)
- User & compute details  
- Query text  
- Query metrics (scan, pruning, etc.)  
- Wall-clock duration (total time)  
- Aggregated task time (parallel execution time)  
- Input / Output data details :contentReference[oaicite:3]{index=3}  

---

## 🔷 Query Profile View (Detailed)

### Left Panel (Tabs)

1. **Details**
   - Summary metrics  

2. **Top Operators**
   - Most expensive operations  
   - Helps optimization  

3. **Query Text**
   - Full SQL query  

---

### Right Panel (DAG View)

- Shows **Directed Acyclic Graph (execution plan)**  
- Visual flow of query execution  

#### Common Operators:
- **Scan** → Read data  
- **Filter** → Apply conditions  
- **Join** → Combine tables  
- **Shuffle** → Data redistribution (expensive)  
- **Aggregate (Hash/Sort)** → Grouping operations :contentReference[oaicite:4]{index=4}  

---

## 🔷 Key Metrics to Analyze

- Time spent per operator  
- Rows processed  
- Memory usage  
- Data scanned  
- Data pruning percentage  

👉 Helps identify:
- Bottlenecks  
- Inefficient operations  

---

## 🔷 Important Notes

- Query profile **not available if query uses cache**  
- Modify query slightly to bypass cache :contentReference[oaicite:5]{index=5}  

---

## 🔷 Sharing Query Profile

- Share via **URL** (with permission)  
- Download as **JSON file** :contentReference[oaicite:6]{index=6}  

---

## 🔷 Import Query Profile

- Upload JSON file  
- View profile locally (not persisted) :contentReference[oaicite:7]{index=7}  

---

## 🔷 Where Else You Can Access It

- SQL Editor  
- Notebooks  
- Jobs UI  
- Pipeline UI :contentReference[oaicite:8]{index=8}  

---

## 🔷 Interview Quick Points

- Query Profile = **Execution analysis tool**  
- Shows **DAG + metrics**  
- Used for **performance tuning**  
- Helps detect:
  - Shuffle issues  
  - Skew  
  - Full scans  

## 🔷 One-line Memory Trick

**Query Profile = “X-ray of your SQL query performance”**

</details>

<summary>Databricks Deletion Vectors</summary>
<details># Databricks Deletion Vectors – Concise Summary

## 🔷 What are Deletion Vectors?

- A **Delta Lake optimization feature**
- Avoids rewriting entire Parquet files for row-level changes  
- Instead of rewriting → **marks rows as deleted/updated**

👉 Normal behavior:
- DELETE → rewrite full file ❌  

👉 With Deletion Vectors:
- DELETE/UPDATE/MERGE → mark rows only ✅  


## 🔷 Why they are used

- Improve performance of:
  - DELETE  
  - UPDATE  
  - MERGE  

- Reduce:
  - File rewrite cost  
  - I/O overhead  

👉 Reads apply these “marked changes” dynamically  

## 🔷 How it works (Simple)

1. Data stored in Parquet files  
2. Instead of modifying file:
   - Store **deletion vector (metadata)**  
3. During read:
   - System applies deletion vector  
   - Shows correct data  

👉 Think: **Soft delete instead of physical rewrite**

## 🔷 When physical changes happen

Data is actually rewritten only during:

- `OPTIMIZE`  
- Auto-compaction  
- `REORG TABLE ... APPLY (PURGE)`  

👉 Old data removed permanently using:

```sql
VACUUM table_name;</details>


<summary>Making<\summary>
<details>
# Databricks Unity Catalog: Row Filters and Column Masks

## Overview
Row filters and column masks in Unity Catalog are used to control access to sensitive data at query time. They enable fine-grained data security without modifying the underlying tables.

---

## Row Filters

### What are Row Filters?
Row filters restrict which rows a user can access in a table based on defined conditions.

- Evaluated at query time
- Returns only rows that meet the condition
- Used for **row-level security**

### Example Use Cases
- Restrict data by region (e.g., user sees only APAC data)
- Limit access by department or account

### Key Features
- Defined using **SQL User-Defined Functions (UDFs)**
- Can include Python or Scala logic (wrapped in SQL UDF)
- One row filter per table
- Can be applied:
  - Per table
  - Centrally via **ABAC policies**

---

## Column Masks

### What are Column Masks?
Column masks control what values users see in specific columns.

- Applied at query time
- Replaces actual column values with masked/transformed values
- Used for **column-level security**

### Example Use Cases
- Mask email addresses
- Hide SSN or sensitive identifiers
- Show partial or obfuscated data

### Key Features
- Defined using **SQL UDFs**
- Must return the same data type as the column
- Can use other columns as inputs
- One mask per column
- Can be applied:
  - Per table
  - Via **ABAC policies**

---

## Row Filters vs Column Masks vs Dynamic Views

| Feature        | Applies To | Managed Using | Naming Impact | Best Use Case |
|----------------|-----------|--------------|--------------|--------------|
| Dynamic Views  | Views     | SQL logic    | New object   | Multi-table filtering, data sharing |
| Row Filters    | Tables    | ABAC / mapping tables | No change | Row-level access control |
| Column Masks   | Columns   | ABAC / mapping tables | No change | Masking sensitive column data |

### When to Use What
- Use **Dynamic Views** for multi-table logic or sharing
- Use **Row Filters & Column Masks** for direct table-level security

---

## How to Apply Filters and Masks

### 1. Using ABAC Policies (Recommended)
- Centralized governance using **governed tags**
- Scales across catalogs and schemas
- More secure (cannot be overridden by table owners)
- Better performance

### 2. Manual Assignment
- Apply directly to tables/columns
- Uses UDFs and mapping tables
- More flexible but harder to maintain

---

## Performance Best Practices

- Use **simple expressions** (avoid complex logic)
- Avoid excessive column masks
- Minimize function arguments
- Avoid too many AND conditions in filters
- Use **deterministic expressions**
- Prefer **SQL UDFs over Python UDFs**
- Test queries for performance impact

---

## Limitations

- Not supported in runtimes below **12.2 LTS**
- Cannot be applied to **views**
- Not supported for **Managed Iceberg tables**
- Not supported via:
  - Delta Lake APIs
  - Unity REST APIs
- No support for:
  - Time travel
  - Table cloning
  - Path-based access

### Additional Constraints
- Only **one row filter per table**
- Each column can have **one mask**
- Cannot reference tables that also have filters/masks
- Limited support in MERGE, UPDATE, DELETE (based on runtime)

---

## Key Takeaways

- Row filters = **control rows**
- Column masks = **control column values**
- Both operate **at query time**
- Use **ABAC policies** for scalability and governance
- Balance **security vs performance**

---

## References
- Databricks Documentation (Unity Catalog Filters and Masks)

# Databricks Unity Catalog - Commands (Row Filters & Column Masks)

## 1. Create a Row Filter Function

CREATE FUNCTION filter_by_region(region STRING)
RETURN current_user() = 'admin' OR region = 'APAC';

---

## 2. Apply Row Filter to a Table

ALTER TABLE sales_data
SET ROW FILTER filter_by_region ON (region);

---

## 3. Drop Row Filter from Table

ALTER TABLE sales_data
DROP ROW FILTER;

---

## 4. Replace Existing Row Filter

ALTER TABLE sales_data
SET ROW FILTER new_filter_function ON (region);

---

## 5. Create a Column Mask Function

CREATE FUNCTION mask_email(email STRING)
RETURN CASE 
    WHEN current_user() = 'admin' THEN email
    ELSE '****@****.com'
END;

---

## 6. Apply Column Mask to a Column

ALTER TABLE customers
ALTER COLUMN email
SET MASK mask_email;

---

## 7. Drop Column Mask

ALTER TABLE customers
ALTER COLUMN email
DROP MASK;

---

## 8. Replace Column Mask

ALTER TABLE customers
ALTER COLUMN email
SET MASK new_mask_function;

---

## 9. Show Functions

SHOW USER FUNCTIONS;

---

## 10. Describe Function

DESCRIBE FUNCTION filter_by_region;

---

## 11. Drop Function

DROP FUNCTION filter_by_region;

---

## 12. Check Applied Filters & Masks

DESCRIBE TABLE EXTENDED sales_data;

---

## 13. Example with Multiple Columns in Mask

CREATE FUNCTION mask_sensitive_data(email STRING, country STRING)
RETURN CASE 
    WHEN country = 'US' THEN email
    ELSE 'REDACTED'
END;

ALTER TABLE customers
ALTER COLUMN email
SET MASK mask_sensitive_data;

---

## Notes

- Only **one row filter per table**
- Only **one mask per column**
- Functions must return:
  - BOOLEAN → for row filters
  - SAME DATA TYPE → for column masks
- Prefer **SQL UDFs** over Python UDFs for performance
</details>



