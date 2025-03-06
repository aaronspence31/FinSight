#!/bin/bash

# Script to stop only active Glue jobs with full pagination support
# Works with thousands of jobs and job runs

echo "Starting Glue job cancellation process..."

# Function to get all job names with pagination
get_all_jobs() {
    local all_jobs=""
    local next_token=""
    
    while true; do
        if [ -z "$next_token" ]; then
            response=$(aws glue list-jobs --max-results 200)
        else
            response=$(aws glue list-jobs --max-results 200 --next-token "$next_token")
        fi
        
        # Extract job names using text output and query
        jobs=$(echo "$response" | aws glue list-jobs --max-results 200 $([ -n "$next_token" ] && echo "--next-token $next_token") --output text --query 'JobNames')
        all_jobs="$all_jobs $jobs"
        
        # Get next token
        next_token=$(echo "$response" | grep -o '"NextToken": "[^"]*"' | cut -d'"' -f4)
        if [ -z "$next_token" ]; then
            break
        fi
    done
    
    echo $all_jobs
}

# Function to get only active job runs with pagination
get_active_job_runs() {
    local job_name="$1"
    local all_runs=""
    local next_token=""
    
    while true; do
        if [ -z "$next_token" ]; then
            response=$(aws glue get-job-runs --job-name "$job_name" --max-results 200 2>/dev/null)
        else
            response=$(aws glue get-job-runs --job-name "$job_name" --max-results 200 --next-token "$next_token" 2>/dev/null)
        fi
        
        # Check if command succeeded
        if [ $? -ne 0 ]; then
            echo "Error fetching job runs for $job_name"
            return
        fi
        
        # Extract ONLY ACTIVE job run IDs using text output and query
        # Filter for job runs in STARTING, RUNNING, STOPPING, WAITING, or SUBMITTED states
        runs=$(echo "$response" | aws glue get-job-runs --job-name "$job_name" --max-results 200 $([ -n "$next_token" ] && echo "--next-token $next_token") --output text --query 'JobRuns[?State==`STARTING` || State==`RUNNING` || State==`STOPPING` || State==`WAITING` || State==`SUBMITTED`].Id' 2>/dev/null)
        all_runs="$all_runs $runs"
        
        # Get next token
        next_token=$(echo "$response" | grep -o '"NextToken": "[^"]*"' | cut -d'"' -f4)
        if [ -z "$next_token" ]; then
            break
        fi
    done
    
    echo $all_runs
}

# Get all job names
echo "Listing all Glue jobs (with pagination)..."
jobs=$(get_all_jobs)
jobs=$(echo "$jobs" | tr -s ' ' | xargs)  # Clean up spaces

if [ -z "$jobs" ]; then
    echo "No Glue jobs found."
    exit 0
fi

echo "Found jobs: $jobs"
job_count=$(echo "$jobs" | wc -w)
echo "Total jobs found: $job_count"

# Process each job
job_counter=0
active_runs_total=0
for job in $jobs; do
    job_counter=$((job_counter + 1))
    echo "======================================================="
    echo "Processing job $job_counter/$job_count: $job"
    
    # Get all ACTIVE job runs with pagination
    echo "Fetching active job runs (with pagination)..."
    run_ids=$(get_active_job_runs "$job")
    run_ids=$(echo "$run_ids" | tr -s ' ' | xargs)  # Clean up spaces
    
    if [ -z "$run_ids" ]; then
        echo "No active job runs found for $job"
        continue
    fi
    
    # Count job runs
    run_count=$(echo "$run_ids" | wc -w)
    active_runs_total=$((active_runs_total + run_count))
    echo "Found $run_count active job runs for $job"
    
    # Stop each job run
    run_counter=0
    for run_id in $run_ids; do
        run_counter=$((run_counter + 1))
        echo "[$job_counter/$job_count] Stopping job run $run_counter/$run_count: $run_id"
        aws glue batch-stop-job-run --job-name "$job" --job-run-ids "$run_id"
        
        # Check status
        if [ $? -eq 0 ]; then
            echo "Successfully requested stop for job run $run_id"
        else
            echo "Failed to stop job run $run_id"
        fi
        
        # Small delay to avoid rate limiting
        sleep 0.2
    done
    
    echo "Completed processing for job: $job"
done

echo "======================================================="
echo "Job cancellation process completed"
echo "Total active job runs stopped: $active_runs_total"