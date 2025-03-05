import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, LongType
import logging


def process_financial_data():
    """
    Simplified ETL job to process financial data from CSV to Parquet.
    Uses AWS Glue DynamicFrames for processing and keeps the structure simple without partitioning.
    """
    # Initialize logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)

    logger.info("Starting simplified financial data ETL job using DynamicFrames")

    # Initialize Glue context
    args = getResolvedOptions(sys.argv, ["JOB_NAME", "input_bucket", "output_bucket"])

    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    job = Job(glueContext)
    job.init(args["JOB_NAME"], args)

    # Set input and output paths
    input_bucket = args["input_bucket"]
    output_bucket = args["output_bucket"]

    if not input_bucket.endswith("/"):
        input_bucket += "/"
    if not output_bucket.endswith("/"):
        output_bucket += "/"

    output_path = f"{output_bucket}processed_outputs"

    logger.info(f"Input bucket: {input_bucket}")
    logger.info(f"Output path: {output_path}")

    try:
        # Read data from S3 using Glue's CSV reader
        logger.info("Reading CSV files from raw data bucket")
        csv_dyf = glueContext.create_dynamic_frame.from_options(
            connection_type="s3",
            connection_options={
                "paths": [input_bucket],
                "recurse": True,
                "groupFiles": "inPartition",
                "groupSize": "1048576",  # 1MB
            },
            format="csv",
            format_options={"withHeader": True, "separator": ","},
        )

        # Log record count
        record_count = csv_dyf.count()
        logger.info(f"Read {record_count} records from source")

        if record_count == 0:
            logger.warning("No data to process. Exiting.")
            job.commit()
            return

        # Convert to DataFrame for transformations
        df = csv_dyf.toDF()

        # Validate required columns
        required_columns = ["date", "symbol", "open", "high", "low", "close", "volume"]
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in input data")

        # Perform basic transformations - just type casting
        logger.info("Casting columns to appropriate data types")
        df = df.withColumn("open", F.col("open").cast(DoubleType()))
        df = df.withColumn("high", F.col("high").cast(DoubleType()))
        df = df.withColumn("low", F.col("low").cast(DoubleType()))
        df = df.withColumn("close", F.col("close").cast(DoubleType()))
        df = df.withColumn("volume", F.col("volume").cast(LongType()))

        # Convert back to DynamicFrame for writing
        dyf = DynamicFrame.fromDF(df, glueContext, "transformed_data")

        logger.info(f"Writing {dyf.count()} records to {output_path}")

        # Write the processed data using DynamicFrame writer without partitioning
        glueContext.write_dynamic_frame.from_options(
            frame=dyf,
            connection_type="s3",
            connection_options={"path": output_path},
            format="parquet",
            format_options={"compression": "snappy"},
            transformation_ctx="write_parquet",
        )

        logger.info("ETL job completed successfully")

    except Exception as e:
        logger.error(f"ETL job failed: {str(e)}")
        raise
    finally:
        # Commit the job regardless of success or failure to ensure proper cleanup
        job.commit()


if __name__ == "__main__":
    process_financial_data()
