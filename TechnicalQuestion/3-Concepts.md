<summary>Expectations: data quality rules applied inside a pipeline.</summary>
<details>
URL: https://docs.databricks.com/aws/en/ldp/expectations?utm_source=chatgpt.com&language=SQL
Expectation decorators come after a @dp.table(), @dp.materialized_view or @dp.temporary_view() decorator and before a dataset definition function, as in the following example:
<img width="2322" height="680" alt="image" src="https://github.com/user-attachments/assets/f845dd53-29ad-44e1-9edc-f6721deed934" />
Fail on invalid records
<img width="1896" height="1048" alt="image" src="https://github.com/user-attachments/assets/15f8b2c0-4c3a-4dc9-9994-807207a4962a" />
Multiple expectations management
<img width="2700" height="1170" alt="image" src="https://github.com/user-attachments/assets/d5d29a2d-3553-4e8f-a4f5-33fad0667827" />

#### Think of them like:
 - “age must be between 0 and 120”
 - “id should not be null”
 - “price > 0”
 
#### Where Expectations are used
They can be applied to:
 - Streaming tables
 - Materialised views
 - Temporary views
   
#### Core Concept (3 Parts) : Each expectation has:
 
- 1. Name (description)
  - Unique per dataset
  - Used for tracking metrics like "valid_customer_age"

- 2. Constraint (logic)
  - SQL Boolean condition
  - Must return TRUE / FALSE : Example: "Age must be between 0 and 120."
- 3. Action (what happens if it fails)
 
Types of Expectation Actions : Databricks provides 3 behaviours:
1. @dp.expect → Keep invalid rows (default)
Data is NOT removed
Metrics are recorded (valid vs invalid)
👉 Use when: You want monitoring only

3. @dp.expect_or_drop → 🗑️ Drop bad rows
Invalid records are removed before writing
Metrics are still recorded
👉 Use when: You want clean datasets

3. @dp.expect_or_fail → Fail pipeline
Pipeline stops immediately
No output is written
👉 Use when: Data quality is critical
**
Python and SQL Syntax**
CONSTRAINT valid_age EXPECT (age BETWEEN 0 AND 120),
CONSTRAINT valid_id EXPECT (id IS NOT NULL)
@dp.expect("valid_age", "age BETWEEN 0 AND 120")
@dp.expect("valid_id", "id IS NOT NULL")

CONSTRAINT valid_age EXPECT (age BETWEEN 0 AND 120),
CONSTRAINT valid_id EXPECT (id IS NOT NULL)

rules = {
  "valid_age": "age BETWEEN 0 AND 120",
  "valid_id": "id IS NOT NULL"
}

@dp.expect_all(rules)

CONSTRAINT valid_age EXPECT (age BETWEEN 0 AND 120) ON VIOLATION DROP ROW,
CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW
@dp.expect_all_or_drop(rules)

CONSTRAINT valid_age EXPECT (age BETWEEN 0 AND 120) ON VIOLATION FAIL UPDATE,
CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION FAIL UPDATE
@dp.expect_all_or_fail(rules)

CREATE OR REFRESH STREAMING TABLE customers (
  CONSTRAINT valid_age EXPECT (age BETWEEN 0 AND 120),
  CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW
)
AS SELECT * FROM raw_customers;
from pyspark import pipelines as dp

@dp.table()
@dp.expect("valid_age", "age BETWEEN 0 AND 120")
@dp.expect_or_drop("valid_id", "id IS NOT NULL")
def customers():
    return spark.readStream.table("raw_customers")

</details>

<summary>Streaming Query</summary>
<details>
 # Databricks PySpark Data Processing Guide

## Overview

This document explains a common Databricks PySpark pattern for:

* Reading data from a table
* Filtering records
* Removing duplicates
* Writing results to another table

## Original Code

```python
spark.table("stream_sink") \
    .filter("recent = true") \
    .dropDuplicates(["item_id", "item_timestamp"]) \
    .write \
    .mode("overwrite") \
    .table("stream_data_stage")
```

## Step-by-Step Explanation

### 1. Read Source Table

Loads an existing table into a DataFrame.

```python
spark.table("stream_sink")
```

### 2. Filter Records

Keeps only rows where `recent = true`.

```python
.filter("recent = true")
```

### 3. Remove Duplicates

Removes duplicate rows based on a combination of columns.

```python
.dropDuplicates(["item_id", "item_timestamp"])
```

### 4. Write Data

Writes the processed data into a target table.

```python
.write.mode("overwrite").table("stream_data_stage")
```

* `overwrite` replaces existing data

## Equivalent SQL

```sql
CREATE OR REPLACE TABLE stream_data_stage AS
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY item_id, item_timestamp) AS rn
    FROM stream_sink
    WHERE recent = true
) t
WHERE rn = 1;
```

## Variations

### Write Modes

#### Append

```python
.write.mode("append").table("stream_data_stage")
```

#### Overwrite with Schema Change

```python
.write.mode("overwrite") \
.option("overwriteSchema", "true") \
.table("stream_data_stage")
```

#### Ignore

```python
.write.mode("ignore").table("stream_data_stage")
```

#### Error (Default)

```python
.write.mode("error").table("stream_data_stage")
```

## Using Column Expressions

```python
from pyspark.sql.functions import col

spark.table("stream_sink") \
    .filter(col("recent") == True) \
    .dropDuplicates(["item_id", "item_timestamp"]) \
    .write.mode("overwrite") \
    .table("stream_data_stage")
```

## Selecting Specific Columns

```python
spark.table("stream_sink") \
    .filter("recent = true") \
    .select("item_id", "item_timestamp", "price") \
    .dropDuplicates(["item_id", "item_timestamp"]) \
    .write.mode("overwrite") \
    .table("stream_data_stage")
```

## Partitioned Write

```python
.write \
.partitionBy("item_timestamp") \
.mode("overwrite") \
.table("stream_data_stage")
```

## Advanced Deduplication (Latest Record)

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, col

window = Window.partitionBy("item_id").orderBy(col("item_timestamp").desc())

df = spark.table("stream_sink") \
    .filter("recent = true") \
    .withColumn("rn", row_number().over(window)) \
    .filter("rn = 1") \
    .drop("rn")

df.write.mode("overwrite").table("stream_data_stage")
```

## Streaming Version

```python
spark.readStream.table("stream_sink") \
    .filter("recent = true") \
    .dropDuplicates(["item_id", "item_timestamp"]) \
    .writeStream \
    .outputMode("append") \
    .toTable("stream_data_stage")
```

## Delta Merge (Upsert)

```python
from delta.tables import DeltaTable

target = DeltaTable.forName(spark, "stream_data_stage")

source_df = spark.table("stream_sink").filter("recent = true")

target.alias("t").merge(
    source_df.alias("s"),
    "t.item_id = s.item_id AND t.item_timestamp = s.item_timestamp"
).whenNotMatchedInsertAll().execute()
```

## Temporary View

```python
df = spark.table("stream_sink") \
    .filter("recent = true") \
    .dropDuplicates(["item_id", "item_timestamp"])

df.createOrReplaceTempView("stream_data_stage")
```

## Best Practice Version

```python
from pyspark.sql.functions import col

df = (
    spark.table("stream_sink")
    .filter(col("recent") == True)
    .dropDuplicates(["item_id", "item_timestamp"])
)

df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("stream_data_stage")
```

## Key Notes

* `dropDuplicates()` keeps the first occurrence
* `overwrite` deletes existing data completely
* Use partitioning for performance optimization
* Use window functions for deterministic deduplication

## Summary

This pipeline:

1. Reads data from a source table
2. Filters recent records
3. Removes duplicates
4. Writes clean data into a staging table


</details>

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

