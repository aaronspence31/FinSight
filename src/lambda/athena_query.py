import boto3
import json
import time
import os
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
athena_client = boto3.client("athena")

# Environment variables
database = os.environ["ATHENA_DATABASE"]
workgroup = os.environ["ATHENA_WORKGROUP"]
output_location = f"s3://{os.environ['RESULTS_BUCKET']}"


def lambda_handler(event, context):
    """
    Main Lambda handler for processing Athena queries
    """
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Extract request data
        request_body = (
            json.loads(event["body"])
            if isinstance(event.get("body"), str)
            else event.get("body", {})
        )

        query_type = request_body.get("queryType", "default")
        params = request_body.get("params", {})

        logger.info(f"Query type: {query_type}, Params: {params}")

        # Get the appropriate SQL query
        query_sql = get_query_by_type(query_type, params)
        if not query_sql:
            return build_response(400, {"error": f"Invalid query type: {query_type}"})

        logger.info(f"Executing query: {query_sql}")

        # Execute the query and get results
        query_execution_id = start_query(query_sql)
        status = wait_for_query_completion(query_execution_id)

        if status != "SUCCEEDED":
            return build_response(500, {"error": f"Query failed with status {status}"})

        # Get and process results
        results = get_query_results(query_execution_id)
        processed_results = process_results(results)

        return build_response(200, processed_results)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return build_response(500, {"error": f"Internal server error: {str(e)}"})


def start_query(query_sql):
    """Start Athena query execution"""
    response = athena_client.start_query_execution(
        QueryString=query_sql,
        QueryExecutionContext={"Database": database},
        ResultConfiguration={"OutputLocation": output_location},
        WorkGroup=workgroup,
    )
    return response["QueryExecutionId"]


def wait_for_query_completion(query_execution_id):
    """Wait for Athena query to complete, return final status"""
    status = "RUNNING"
    max_retries = 30
    retries = 0

    while status == "RUNNING" or status == "QUEUED":
        if retries >= max_retries:
            break

        response = athena_client.get_query_execution(
            QueryExecutionId=query_execution_id
        )
        status = response["QueryExecution"]["Status"]["State"]

        if status == "RUNNING" or status == "QUEUED":
            time.sleep(2)  # Wait before checking again
            retries += 1

    return status


def get_query_results(query_execution_id):
    """Get results of a completed Athena query"""
    return athena_client.get_query_results(QueryExecutionId=query_execution_id)


def process_results(results):
    """Process Athena results into a more usable format"""
    columns = [
        col["Label"] for col in results["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
    ]

    data = []
    # Skip the header row if it exists
    start_row = (
        1
        if results["ResultSet"]["Rows"] and len(results["ResultSet"]["Rows"]) > 0
        else 0
    )

    for row in results["ResultSet"]["Rows"][start_row:]:
        values = []
        for field in row["Data"]:
            # Handle various data types that may come from Athena
            value = field.get("VarCharValue", "")
            values.append(value)

        row_data = dict(zip(columns, values))
        data.append(row_data)

    return {"columns": columns, "data": data}


def build_response(status_code, body):
    """Build a properly formatted API Gateway response"""
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # CORS header
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }


def get_query_by_type(query_type, params):
    """Return SQL query based on query type and parameters"""
    # Use safe defaults if parameters aren't provided
    if query_type == "stockTimeSeriesByPartition":
        symbol = params.get("symbol", "AAPL")
        year = params.get("year", 2023)
        month = params.get("month", 1)

        return f"""
            SELECT date, symbol, open, high, low, close, volume 
            FROM stock_data 
            WHERE symbol = '{symbol}' 
            AND year = {year}
            AND month = {month}
            ORDER BY date
        """

    elif query_type == "volumeAnalysisByPartition":
        symbol = params.get("symbol", "AAPL")
        year = params.get("year", 2023)
        month = params.get("month", 1)

        return f"""
            SELECT 
                date,
                symbol,
                volume,
                close
            FROM stock_data
            WHERE symbol = '{symbol}'
            AND year = {year}
            AND month = {month}
            ORDER BY date
        """

    # Default query - simple table preview
    return """
        SELECT * FROM stock_data LIMIT 10
    """
