#!/bin/bash

# Convenience script to start either single or multiple instances
# Usage: 
#   ./start.sh single          - Start single instance
#   ./start.sh multiple [n]    - Start n instances (default 3)
#   ./start.sh [n]             - Start n instances (backward compatibility)

set -e

MODE=${1:-multiple}

case "$MODE" in
    "single")
        echo "Starting in single instance mode..."
        ./start-single.sh
        ;;
    "multiple")
        INSTANCES=${2:-3}
        echo "Starting $INSTANCES instances..."
        ./start-multiple-instances.sh "$INSTANCES"
        ;;
    [0-9]*)
        # Backward compatibility - if first argument is a number, treat as instance count
        INSTANCES=$1
        echo "Starting $INSTANCES instances..."
        ./start-multiple-instances.sh "$INSTANCES"
        ;;
    *)
        echo "Usage: $0 {single|multiple [count]|[count]}"
        echo "Examples:"
        echo "  $0 single          # Start single instance"
        echo "  $0 multiple 5      # Start 5 instances"
        echo "  $0 3               # Start 3 instances (backward compatible)"
        exit 1
        ;;
esac
