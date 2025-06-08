# Enhanced test script for VSCode compatibility

Write-Host "🧪 Testing Database Connections from VSCode..." -ForegroundColor Cyan

# Test PostgreSQL
Write-Host "Testing PostgreSQL..." -ForegroundColor Yellow
try {
    $pgResult = & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d postgres -c "SELECT 1;" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL is running" -ForegroundColor Green
    } else {
        Write-Host "❌ PostgreSQL connection failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ PostgreSQL not found or connection failed" -ForegroundColor Red
}

# Test Redis (Multiple methods)
Write-Host "Testing Redis..." -ForegroundColor Yellow

# Method 1: Try redis-cli from PATH
try {
    $redisResult = redis-cli ping 2>$null
    if ($redisResult -eq "PONG") {
        Write-Host "✅ Redis is running (via PATH)" -ForegroundColor Green
    } else {
        throw "Redis not responding"
    }
} catch {
    # Method 2: Try full path
    try {
        $redisResult = & "C:\Program Files\Redis\redis-cli.exe" ping 2>$null
        if ($redisResult -eq "PONG") {
            Write-Host "✅ Redis is running (via full path)" -ForegroundColor Green
        } else {
            throw "Redis not responding"
        }
    } catch {
        # Method 3: Check if Redis service is running
        $redisService = Get-Service -Name "Redis" -ErrorAction SilentlyContinue
        if ($redisService -and $redisService.Status -eq "Running") {
            Write-Host "⚠️  Redis service is running but CLI connection failed" -ForegroundColor Yellow
            Write-Host "   Try: redis-cli -h 127.0.0.1 -p 6379 ping" -ForegroundColor Cyan
        } else {
            Write-Host "❌ Redis connection failed" -ForegroundColor Red
            Write-Host "   Try starting Redis manually or as service" -ForegroundColor Cyan
        }
    }
}

# Show connection strings for .env
Write-Host "`n📝 Your .env file should contain:" -ForegroundColor Cyan
Write-Host "DATABASE_URL=postgresql://postgres:your_password@localhost:5432/chess4p" -ForegroundColor White
Write-Host "REDIS_URL=redis://localhost:6379/0" -ForegroundColor White
