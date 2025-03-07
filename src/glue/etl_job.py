import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import functions as F


def process(glue_context, input_path, output_path, file_name):
    """
    Process the stock data CSV file and write to S3 as Parquet,
    partitioned by year and month for improved query performance.
    """
    try:
        # Set Spark configuration for Parquet compression
        glue_context.spark_session.conf.set(
            "spark.sql.parquet.compression.codec", "snappy"
        )

        print(f"Processing file: {input_path}{file_name}")

        # Read the CSV data from S3 using Dynamic Frame to allow for schema flexibility
        dynamic_frame = glue_context.create_dynamic_frame.from_options(
            connection_type="s3",
            connection_options={"paths": [f"{input_path}{file_name}"]},
            format="csv",
            format_options={
                "withHeader": True,
                "separator": ",",
            },
        )

        # Convert to DataFrame to apply some specific transformations
        df = dynamic_frame.toDF()

        # Validate if we have data
        if df.count() == 0:
            print("No data found in the input file")
            return

        print(f"Loaded {df.count()} records from CSV")

        # Convert date string to date type
        df = df.withColumn("date", F.to_date(df["date"], "yyyy-MM-dd"))

        # Extract and add year and month columns for partitioning
        df = df.withColumn("year", F.year(df["date"]))
        df = df.withColumn("month", F.month(df["date"]))

        # Convert numeric columns to appropriate types
        numeric_cols = ["open", "high", "low", "close"]
        for col_name in numeric_cols:
            df = df.withColumn(col_name, df[col_name].cast("double"))

        # Cast volume to long for large numbers
        df = df.withColumn("volume", df["volume"].cast("long"))

        # Print schema after transformations performed
        print("Schema after transformations:")
        df.printSchema()

        # Create dynamic frame from dataframe for writing
        # Dynamic Frame is used to write to S3 as we can use the getSink method with dynamic frames
        # to easily write to S3 with partitioning and catalog updates
        dynamic_frame_output = DynamicFrame.fromDF(
            df, glue_context, "dynamic_frame_output"
        )

        print(f"Writing processed data to: {output_path}")

        # Configure the sink with partitioning and catalog updates
        sink = glue_context.getSink(
            connection_type="s3",
            path=output_path,
            enableUpdateCatalog=True,
            updateBehavior="UPDATE_IN_DATABASE",
            partitionKeys=["year", "month"],
            format_options={"compression": "snappy"},
        )
        sink.setCatalogInfo(
            catalogDatabase="finsight_db", catalogTableName="stock_data"
        )
        sink.setFormat(format="glueparquet")

        # Write the data
        sink.writeFrame(dynamic_frame_output)

        print(f"Successfully processed and wrote data to: {output_path}")
        print(f"Data is partitioned by year and month for efficient querying")

    except Exception as e:
        print(f"Error processing data: {str(e)}")
        raise e


def main():
    """Main ETL job function"""
    args = getResolvedOptions(
        sys.argv, ["JOB_NAME", "input_bucket", "output_bucket", "file_name"]
    )
    print("Job Parameters:")
    print(f"  input_bucket: {args['input_bucket']}")
    print(f"  output_bucket: {args['output_bucket']}")
    print(f"  file_name: {args['file_name']}")

    # Initialize Spark and Glue contexts
    sc = SparkContext()
    glue_context = GlueContext(sc)
    job = Job(glue_context)
    job.init(args["JOB_NAME"], args)

    try:
        # Define input and output paths
        input_path = args["input_bucket"]
        output_path = f"{args['output_bucket']}processed_outputs/"
        file_name = args["file_name"]

        print(f"Starting ETL process")
        print(f"Input path: {input_path}{file_name}")
        print(f"Output path: {output_path}")

        # Process the data
        process(glue_context, input_path, output_path, file_name)

        print("ETL job completed successfully")

    except Exception as e:
        print(f"Error in ETL job: {str(e)}")
        raise e
    finally:
        # Clean up job resources
        print("Cleaning up job resources")
        job.commit()
        print("Job resources cleaned up")


if __name__ == "__main__":
    main()
