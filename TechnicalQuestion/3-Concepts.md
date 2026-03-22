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

