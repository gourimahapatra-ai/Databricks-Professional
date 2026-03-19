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

