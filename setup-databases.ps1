# fixed-db-setup.ps1 - Fixed PostgreSQL setup

Write-Host "🐘 Setting up PostgreSQL..." -ForegroundColor Yellow

# Set the password we'll use
$pgPassword = "chess_secure"
$env:PGPASSWORD = $pgPassword

# Check if database already exists
$dbExists = & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -lqt | Select-String "chess4p"

if (-not $dbExists) {
    try {
        & "C:\Program Files\PostgreSQL\17\bin\createdb.exe" -U postgres chess4p
        Write-Host "✅ Database 'chess4p' created" -ForegroundColor Green
    } catch {
        Write-Host "❌ Database creation failed: $_" -ForegroundColor Red
    }
} else {
    Write-Host "ℹ️  Database 'chess4p' already exists" -ForegroundColor Blue
}

# Check if user already exists
$userExists = & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d chess4p -c "SELECT 1 FROM pg_roles WHERE rolname='chessapp'" | Select-String "1"

if (-not $userExists) {
    try {
        & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c "CREATE USER chessapp WITH PASSWORD 'chess_secure';"
        Write-Host "✅ User 'chessapp' created" -ForegroundColor Green
    } catch {
        Write-Host "❌ User creation failed: $_" -ForegroundColor Red
    }
} else {
    Write-Host "ℹ️  User 'chessapp' already exists" -ForegroundColor Blue
}

# Grant permissions
try {
    & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE chess4p TO chessapp;"
    Write-Host "✅ Permissions granted" -ForegroundColor Green
} catch {
    Write-Host "❌ Permission grant failed: $_" -ForegroundColor Red
}

# Test connection with chessapp user
Write-Host "🧪 Testing chessapp connection..." -ForegroundColor Yellow
$env:PGPASSWORD = "chess_secure"
try {
    & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U chessapp -d chess4p -c "SELECT 1;" 2>$null
    Write-Host "✅ chessapp user connection successful" -ForegroundColor Green
} catch {
    Write-Host "❌ chessapp connection failed" -ForegroundColor Red
}

Write-Host "📝 Update your .env file with:" -ForegroundColor Cyan
Write-Host "DATABASE_URL=postgresql://chessapp:chess_secure@localhost:5432/chess4p" -ForegroundColor White
