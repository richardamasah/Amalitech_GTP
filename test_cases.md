#  Test Cases: Real-Time E-Commerce Data Pipeline

This manual test plan verifies the functionality, reliability, and robustness of the real-time data pipeline built using Apache Spark Structured Streaming and PostgreSQL. Each test includes the performed action, the expected output, and the observed result.

---

##  Test 1: CSV File Generation

**Action**  
- Run `python data_generator.py` for 10 seconds.  
- Observe the `data/events/` folder.

**Expected Outcome**  
- At least 2 CSV files created (e.g., `events_174xxxxxx.csv`).  
- Each file contains 10 rows with the following columns:
  - `event_id`, `user_id`, `event_type`, `product_id`, `product_name`, `price`, `timestamp`
- Data is valid:
  - UUIDs for IDs  
  - `event_type` is either `view` or `purchase`  

**Actual Outcome**  
- ✅ Two files created: `events_1749050000.csv`, `events_1749050005.csv`  
- ✅ Each file contains 10 rows with correct schema  
- ✅ Sample data:  
  - `event_id=123e4567-e89b-12d3-a456-426614174000`,  
  - `event_type=view`,  
  - `price=49.99`,  
  - `timestamp=2025-04-15T14:30:00`

---

##  Test 2: Spark Streaming Detection

**Action**  
- Run `data_generator.py` continuously  
- Run `spark-submit spark_streaming_to_postgres.py`  
- Monitor Spark UI (`http://localhost:4040`) and terminal logs  

**Expected Outcome**  
- Spark detects new CSVs every ~5 seconds  
- No schema mismatch or read errors in logs  
- Spark UI shows active streaming query with growing row count  

**Actual Outcome**  
- ✅ Detected 3 CSVs in 15 seconds  
- ✅ Log: “Processing new file: .../events_1749050010.csv”  
- ✅ UI showed 30 rows processed (3 files × 10 rows)  
- ✅ No errors encountered

---

##  Test 3: Data Transformation Validation

**Action**  
- Run both scripts  
- After 10 seconds, query:
  ```sql
  SELECT timestamp, event_type, created_at FROM user_events LIMIT 5;
