#!/bin/bash

# Set up error handling
set -e  # Exit immediately if a command exits with a non-zero status

# Define base commands to run in parallel
# Simply add new commands to this array, one per line
BASE_COMMANDS=(
    "pdm bootloader build --fw-location=spiflash"
    "pdm polysyn build"
    "pdm selftest build"
    "pdm xbeam build"
    "pdm macro_osc build"
    "pdm sid build"
)

# Array to store all background PIDs
PIDS=()
PGIDS=()

# Use a separate process group for each command to enable better cleanup
# This allows killing entire process trees
setup_process_groups() {
    # Make sure script has its own process group
    set -m
}

setup_process_groups

# Run all commands in parallel, appending any additional arguments
echo "Starting commands in parallel..."
for cmd in "${BASE_COMMANDS[@]}"; do
    # Append all command line arguments to each command
    full_cmd="$cmd $*"
    echo "Starting: $full_cmd"
    
    # Run in a separate process group
    (eval "$full_cmd") &
    
    PID=$!
    PIDS+=($PID)
    
    # Get the process group ID
    PGID=$(ps -o pgid= $PID | tr -d ' ')
    PGIDS+=($PGID)
    
    echo "Started process $PID in group $PGID: $full_cmd"
done

# Cleanup function to kill all process groups
cleanup() {
    echo "Cleaning up and killing all process groups..."
    for pgid in "${PGIDS[@]}"; do
        if [ ! -z "$pgid" ]; then
            echo "Killing process group $pgid and all its children..."
            # Kill the entire process group
            kill -TERM -$pgid 2>/dev/null || kill -KILL -$pgid 2>/dev/null || true
        fi
    done
}

# Function to check if a process group is still active
is_pgid_active() {
    local pgid=$1
    ps -o pgid= | grep -q "^[[:space:]]*$pgid$"
    return $?
}

# Set trap for normal exit, interrupts, and errors
trap cleanup EXIT INT TERM

# Flag to track if any command failed
FAILED=0

# Wait for all processes to complete or any to fail
echo "All commands are running in parallel. Waiting for completion..."

# Check processes until all complete or one fails
while [ ${#PIDS[@]} -gt 0 ]; do
    for i in "${!PIDS[@]}"; do
        # Check if process still exists
        if ! kill -0 ${PIDS[$i]} 2>/dev/null; then
            # Process has exited, check its status
            wait ${PIDS[$i]} || {
                echo "Process ${PIDS[$i]} (group ${PGIDS[$i]}) failed!"
                FAILED=1
                break 2  # Exit both loops
            }
            
            echo "Process ${PIDS[$i]} (group ${PGIDS[$i]}) completed successfully"
            unset PIDS[$i]
            unset PGIDS[$i]
        fi
    done
    
    # Re-index the arrays to remove empty slots
    PIDS=("${PIDS[@]}")
    PGIDS=("${PGIDS[@]}")
    
    # Short sleep to avoid CPU spinning
    sleep 0.2
    
    # Break if we detected a failure
    [ $FAILED -eq 1 ] && break
done

# If any command failed, exit with error
if [ $FAILED -eq 1 ]; then
    echo "One or more commands failed. Exiting with error."
    exit 1
fi

# Remove the trap before exiting successfully
trap - EXIT INT TERM

echo "All commands completed successfully."
