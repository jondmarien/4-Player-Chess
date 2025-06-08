# Check if .env exists and what it contains
if (Test-Path .env) {
    Write-Host "✅ .env file exists" -ForegroundColor Green
    Get-Content .env | Write-Host
} else {
    Write-Host "❌ .env file not found" -ForegroundColor Red
}

# Test environment loading
"""
uv run python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('DATABASE_URL from env:', repr(os.getenv('DATABASE_URL')))
print('REDIS_URL from env:', repr(os.getenv('REDIS_URL')))
"
"""
