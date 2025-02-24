#!/bin/bash

# Exit on error
set -e

# Initialize status tracking with simple variables
redis_status="NOT_CHECKED"
postgres_status="NOT_CHECKED"
celery_status="NOT_CHECKED"
fastapi_status="NOT_CHECKED"

# Function to check for duplicate processes
check_duplicates() {
    local service=$1
    local count=$(pgrep -f "$service" | wc -l | tr -d ' ')
    if [ "$count" -gt 1 ]; then
        echo "⚠️  Warning: Found $count $service processes running!"
        echo "Process details:"
        ps aux | grep "$service" | grep -v grep
    fi
}

# Function to check memory usage
check_memory() {
    local pid=$1
    local name=$2
    if [ -n "$pid" ]; then
        echo "Memory usage for $name (PID: $pid):"
        ps -o pid,rss,%mem,command -p "$pid" | tail -n 1
    fi
}

echo "🔍 Checking all backend services..."

# Check Redis
echo -n "Checking Redis... "
if redis-cli ping > /dev/null; then
    echo "✅ Redis is running"
    
    # Enhanced Redis checks
    echo "Redis Health Checks:"
    echo "1. Memory Stats:"
    redis-cli info | grep "used_memory\|maxmemory"
    
    echo "2. Connection Analysis:"
    echo "Total clients: $(redis-cli client list | wc -l | xargs)"
    echo "By connection type:"
    redis-cli client list | grep -o "type=[^ ]*" | sort | uniq -c
    
    echo "3. Blocked/Waiting Clients:"
    redis-cli client list | grep -E "blocked|waiting" || echo "No blocked clients"
    
    echo "4. Memory Usage by Key Space:"
    redis-cli memory stats | grep "keys\|overhead"
    
    # Check for idle connections
    echo "5. Idle Connections (>60s):"
    redis-cli client list | awk -F'[ =]' '/idle/ && $6 > 60 {print $0}' || echo "No idle connections"
    
    echo "\nRecent Redis logs:"
    tail -n 20 logs/redis/redis.log
    
    redis_status="OK"
else
    echo "❌ Redis is not responding"
    redis_status="FAILED"
fi

# Check PostgreSQL
echo -n "Checking PostgreSQL... "
if pg_isready -h localhost -U tom -d content_platform > /dev/null 2>&1; then
    echo "✅ PostgreSQL is running"
    
    echo "PostgreSQL Health Checks:"
    echo "1. Active Connections:"
    psql -h localhost -U tom -d content_platform -c "
        SELECT datname, count(*) as connections,
            sum(case when state = 'idle' then 1 else 0 end) as idle,
            sum(case when state = 'active' then 1 else 0 end) as active
        FROM pg_stat_activity 
        GROUP BY datname;"
    
    echo "2. Long-running Queries (>30s):"
    psql -h localhost -U tom -d content_platform -c "
        SELECT pid, now() - query_start as duration, state, query 
        FROM pg_stat_activity 
        WHERE state != 'idle' 
        AND now() - query_start > interval '30 seconds';"
    
    echo "3. Database Size:"
    psql -h localhost -U tom -d content_platform -c "
        SELECT pg_size_pretty(pg_database_size('content_platform'));"
    
    postgres_status="OK"
else
    echo "❌ PostgreSQL is not responding"
    postgres_status="FAILED"
fi

# Check Celery
echo -n "Checking Celery worker... "
if [ -f "logs/celery.pid" ]; then
    CELERY_PID=$(cat logs/celery.pid)
    if ps -p $CELERY_PID > /dev/null; then
        echo "✅ Celery worker is running (PID: $CELERY_PID)"
        
        echo "Celery Health Checks:"
        echo "1. Memory Usage:"
        check_memory "$CELERY_PID" "Celery"
        
        echo "2. Active Tasks:"
        celery -A tasks inspect active 2>/dev/null || echo "Could not fetch active tasks"
        
        echo "3. Reserved Tasks:"
        celery -A tasks inspect reserved 2>/dev/null || echo "Could not fetch reserved tasks"
        
        echo "4. Check for duplicate workers:"
        check_duplicates "celery"
        
        echo "\nRecent Celery logs:"
        tail -n 20 logs/celery/worker.log
        
        celery_status="OK"
    else
        echo "❌ Celery worker is not running"
        celery_status="FAILED"
    fi
else
    echo "❌ Celery PID file not found"
    celery_status="FAILED"
fi

# Check FastAPI/Uvicorn
echo -n "Checking FastAPI/Uvicorn... "
if [ -f "logs/uvicorn.pid" ]; then
    UVICORN_PID=$(cat logs/uvicorn.pid)
    if ps -p $UVICORN_PID > /dev/null; then
        echo "✅ FastAPI is running (PID: $UVICORN_PID)"
        
        echo "FastAPI Health Checks:"
        echo "1. Memory Usage:"
        check_memory "$UVICORN_PID" "Uvicorn"
        
        echo "2. Check for duplicate instances:"
        check_duplicates "uvicorn"
        
        echo "3. Open Connections:"
        lsof -p "$UVICORN_PID" | grep "TCP" || echo "No open connections"
        
        echo "4. API Health Check:"
        curl -s http://localhost:8000/health || echo "❌ Health endpoint not responding"
        
        echo "\nRecent FastAPI logs:"
        tail -n 20 logs/backend/uvicorn.log
        
        fastapi_status="OK"
    else
        echo "❌ FastAPI is not running"
        fastapi_status="FAILED"
    fi
else
    echo "❌ Uvicorn PID file not found"
    fastapi_status="FAILED"
fi

# Print summary
echo ""
echo "📊 Services Status Summary:"
echo "=========================="
failed_services=""

# Check each service status
[ "$redis_status" != "OK" ] && failed_services="$failed_services redis"
[ "$postgres_status" != "OK" ] && failed_services="$failed_services postgres"
[ "$celery_status" != "OK" ] && failed_services="$failed_services celery"
[ "$fastapi_status" != "OK" ] && failed_services="$failed_services fastapi"

# Print status for each service
[ "$redis_status" = "OK" ] && echo "✅ Redis: Running" || echo "❌ Redis: Not running"
[ "$postgres_status" = "OK" ] && echo "✅ PostgreSQL: Running" || echo "❌ PostgreSQL: Not running"
[ "$celery_status" = "OK" ] && echo "✅ Celery: Running" || echo "❌ Celery: Not running"
[ "$fastapi_status" = "OK" ] && echo "✅ FastAPI: Running" || echo "❌ FastAPI: Not running"

# Print final verdict
echo ""
if [ -z "$failed_services" ]; then
    echo "✨ All services are running properly! ✨"
else
    echo "⚠️  The following services need attention:$failed_services"
    echo "Run './start.sh' to restart all services"
fi

# Resource Waste Analysis
echo ""
echo "🔍 Resource Waste Analysis:"
echo "=========================="

# Function to format memory in human readable format
format_memory() {
    local mem=$1
    if [ $mem -gt 1048576 ]; then
        echo "$(( mem / 1048576 ))GB"
    elif [ $mem -gt 1024 ]; then
        echo "$(( mem / 1024 ))MB"
    else
        echo "${mem}KB"
    fi
}

# Collect findings
findings=()

# Check Redis memory efficiency
redis_used_mem=$(redis-cli info memory | grep "used_memory:" | cut -d: -f2)
redis_peak_mem=$(redis-cli info memory | grep "used_memory_peak:" | cut -d: -f2)
redis_fragmentation=$(redis-cli info memory | grep "mem_fragmentation_ratio:" | cut -d: -f2)
if (( $(echo "$redis_fragmentation > 1.5" | bc -l) )); then
    findings+=("Redis memory fragmentation ratio is high: ${redis_fragmentation}")
fi

# Check for idle Redis connections
idle_connections=$(redis-cli client list | awk -F'[ =]' '/idle/ && $6 > 300 {count++} END {print count}')
if [ "$idle_connections" -gt 5 ]; then
    findings+=("Found ${idle_connections} Redis connections idle for >5 minutes")
fi

# Check PostgreSQL connection efficiency
pg_max_connections=$(psql -h localhost -U tom -d content_platform -tAc "SHOW max_connections;")
pg_active_connections=$(psql -h localhost -U tom -d content_platform -tAc "SELECT count(*) FROM pg_stat_activity;")
pg_usage_ratio=$(echo "scale=2; $pg_active_connections / $pg_max_connections * 100" | bc)
if [ $(echo "$pg_usage_ratio < 10" | bc -l) -eq 1 ]; then
    findings+=("PostgreSQL connection usage is low (${pg_usage_ratio}%) - consider reducing max_connections")
fi

# Check for duplicate processes
for service in "celery" "uvicorn" "redis-server"; do
    count=$(pgrep -f "$service" | wc -l | tr -d ' ')
    if [ "$count" -gt 1 ]; then
        findings+=("Found ${count} instances of ${service} running")
    fi
done

# Check for memory-hungry processes
for pid in $CELERY_PID $UVICORN_PID; do
    if [ -n "$pid" ]; then
        mem_usage=$(ps -o rss= -p "$pid" | tr -d ' ')
        if [ "$mem_usage" -gt 524288 ]; then # 512MB
            process_name=$(ps -p "$pid" -o comm=)
            findings+=("${process_name} (PID: ${pid}) using $(format_memory $mem_usage) of RAM")
        fi
    fi
done

# Print findings
if [ ${#findings[@]} -eq 0 ]; then
    echo "✅ No resource waste detected"
else
    echo "⚠️  Resource waste findings:"
    for finding in "${findings[@]}"; do
        echo "  • $finding"
    done
    echo ""
    echo "💡 Recommendations:"
    echo "  • Run cleanup.sh to remove duplicate processes"
    echo "  • Consider restarting services showing high memory usage"
    echo "  • Review connection pooling settings if seeing many idle connections"
fi
