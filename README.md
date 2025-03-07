# FinSight

FinSight is an AWS serverless ETL pipeline that transforms financial data so that it can be queried quickly, especially when filtered by year and month, complete with an interactive analytics dashboard which queries the transformed data.

## How It Works

- **Data Ingestion**: Upload CSV files with financial data to an S3 bucket to trigger the entire process automatically.
- **Serverless Processing**: A notification system activates Lambda functions that kick off the ETL workflow.
- **Data Transformation**: Behind the scenes, AWS Glue transforms raw data into an optimized format with intelligent partitioning for high-performance querying.
- **Analytics Interface**: Query the processed data using standard SQL through Athena, with improved performance compared to querying raw files.
- **Visualization**: Explore financial data through a simple web dashboard that demonstrates how the optimized data structure enables faster analytics.

## The ETL Pipeline

### Extract

- S3 immediately alerts Lambda when a new CSV arrives in the input bucket.
- Lambda records the file details and kicks off the Glue ETL process.

### Transform

- **Format and Type Conversions**: Cleans up dates and numeric fields for consistent analytics.
- **Partitioning**: Automatically groups data by year and month for faster queries.
- **Optimized Storage**: Converts CSV files into compressed Parquet files.
- **Automatic Schema Updates**: Keeps Glue Data Catalog updated effortlessly. We should not have any issues when querying as long as the data types for all columns remain consistent (if they are not consistent you might get query failures or unexpected type conversions if Athena is not able to infer the correct type). Columns can be added or removed between schema updates, however, our ETL transformations do require certain core columns (date, price fields, volume) to be present in all input data.

### Load

- Transformed data lands in S3, neatly organized in folders like `/year=YYYY/month=MM/`.
- Athena immediately picks up on these changes, so data is ready to query instantly.

## AWS Infrastructure

- **S3**: Handles raw CSV inputs, processed outputs, and hosts static web content.
- **Lambda**: Manages file uploads and Athena queries.
- **Glue**: Serverless ETL.
- **Athena**: Offers SQL querying of processed and unprocessed data in S3.
- **API Gateway**: Makes sure web interface communicates securely with backend services.

## Next Steps

### Data Warehouse Integration

The current implementation successfully demonstrates a data lake architecture with S3 and Athena where we go from S3 to S3. A logical next step would be to integrate with Amazon Redshift to:

- Support more complex analytical queries that benefit from Redshift's columnar storage and distributed query execution
- Enable more concurrent users as the dashboard usage grows

### Enhanced ETL Processing

Building on the current Glue ETL job, future enhancements could include:

- Implement more sophisticated transformations using AWS Glue
- Create additional partitioning schemes based on other query patterns
- Try using Amazon EMR (Elastic MapReduce) for more complex transformations that require fine-tuned control over the Spark environment

## FinSight Demonstration

### Triggering the ETL Pipeline

![Uploading CSV to S3](./assets/upload-csv.png)
_Step 1: Uploading a CSV file to the input S3 bucket triggers the automated ETL process._

![Glue Job Automatically Triggered](./assets/triggered-glue-job.png)
_Step 2: The AWS Glue ETL job is automatically triggered through a Lambda function, beginning the data transformation process._

### Raw Input Data

![Raw Input Data Size in S3](./assets/raw-input-data-size.png)
_The raw financial data in the input bucket takes up 1.9GB of storage space._

![Raw Input Data in S3](./assets/raw-input-data.png)
_The raw financial data is initially stored as CSV files in the input S3 bucket, which is not optimized querying._

Example of a CSV file:

```
date,symbol,open,high,low,close,volume
2023-01-03,AAPL,130.28,130.90,124.17,125.07,112117500
2023-01-04,AAPL,126.89,128.66,125.08,126.36,89113600
```

#### Raw Data Table Definition

The raw data is made accessible in Athena through the following table definition:

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS raw_stock_data (
    date STRING,
    symbol STRING,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume BIGINT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 's3://finsight-dev-raw-input-xxxxx/'
TBLPROPERTIES ("skip.header.line.count"="1");
```

This table definition points directly to the CSV files in the input S3 bucket, allowing Athena to query the raw data without any optimizations.

### Processed Data with Partitioning

![Processed Data Size in S3](./assets/output-data-size.png)
_After transformation, the data size is reduced from 1.9GB to 745MB, demonstrating the efficiency of Parquet format._

![Processed Data in Parquet Format](./assets/output-data-parquet.png)
_The transformed data is stored in the efficient Parquet format, which is columnar and compressed._

![Year-based Partitioning](./assets/output-data-year-filtering-in-s3.png)
_Data is partitioned by year, allowing for efficient filtering of queries by year._

![Month-based Partitioning](./assets/output-data-month-filtering-in-s3.png)
_Further partitioning by month (`/year=YYYY/month=MM/`) improves query performance by allowing Athena to scan only relevant partitions._

### Query Performance Comparison

#### Query on Raw Data

The following query runs on the raw, unoptimized CSV data:

```sql
SELECT
    date,
    AVG(close) as avg_close,
    SUM(volume) as total_volume,
    COUNT(DISTINCT symbol) as symbol_count
FROM
    raw_stock_data
WHERE
    date LIKE '2024-02%'
GROUP BY
    date
ORDER BY
    date;
```

![Athena Query Performance on Raw Data](./assets/input-data-athena-query-performance.png)
_Querying the raw data requires Athena to scan the entire dataset, even though we're only interested in February 2024 data. This results in slower performance and higher costs. You can see this as the input rows in the image are 39.31M and 85% of the total runtime is spent in execution._

#### Query on Processed Data

The same query on the processed, partitioned Parquet data:

```sql
SELECT
    date,
    AVG(close) as avg_close,
    SUM(volume) as total_volume,
    COUNT(DISTINCT symbol) as symbol_count
FROM
    stock_data
WHERE
    year = 2024 AND
    month = 2
GROUP BY
    date
ORDER BY
    date;
```

![Athena Query Performance on Processed Data](./assets/output-data-athena-query-performance.png)
_Querying the processed data is significantly faster because Athena only needs to scan the relevant partition (year=2024, month=2) rather than the entire dataset.You can see this as the input rows are now 210K rather than 39.31M and the execution time is only 53% while more time is spent planning now. The total runtime for the query dropped from 1.9 to 1.3 seconds and this differnece in performance should only grow as we store more data._

### Interactive Dashboard

![Web Dashboard Overview](./assets/web-dashboard-one.png)
_The web dashboard provides an overview of stock performance across all companies, leveraging the optimized data structure._

![Web Dashboard Apple Details](./assets/web-dashboard-two.png)
_Detailed view of Apple stock performance. The dashboard executes queries that take advantage of the year/month partitioning, delivering fast insights from the financial data._
