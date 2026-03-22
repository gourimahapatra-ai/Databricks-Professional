<summary>Expectations: data quality rules applied inside a pipeline.</summary>
<details>
URL: https://docs.databricks.com/aws/en/ldp/expectations?utm_source=chatgpt.com
Expectation decorators come after a @dp.table(), @dp.materialized_view or @dp.temporary_view() decorator and before a dataset definition function, as in the following example:
### Think of them like:
 - “age must be between 0 and 120”
 - “id should not be null”
 - “price > 0”
### Where Expectations are used
They can be applied to:
 - Streaming tables
 - Materialised views
 - Temporary views
### Core Concept (3 Parts) : Each expectation has:
- 1. Name (description)
  - Unique per dataset
  - Used for tracking metrics like "valid_customer_age"

- 2. Constraint (logic)
  - SQL Boolean condition
  - Must return TRUE / FALSE : Example: "Age must be between 0 and 120."
- 3. Action (what happens if it fails)
</details>

