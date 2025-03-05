import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import functions as F

# Get job parameters
args = getResolvedOptions(sys.argv, ["JOB_NAME", "input_file_path"])

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Extract the bucket and key from the input path
input_path = args["input_file_path"]
print(f"Processing input file: {input_path}")

# Read the CSV file
df = spark.read.option("header", "true").csv(input_path)

# Perform transformations
# For example, calculate financial metrics
df = df.withColumn("formatted_date", F.to_date(F.col("date"), "yyyy-MM-dd"))
df = df.withColumn("year", F.year(F.col("formatted_date")))
df = df.withColumn("month", F.month(F.col("formatted_date")))

# Write the processed data to the output bucket
output_path = input_path.replace("raw-input", "processed-output").replace(".csv", "")
df.write.mode("overwrite").parquet(f"{output_path}/")

# Log completion
print(f"ETL job completed. Data written to: {output_path}")

job.commit()
