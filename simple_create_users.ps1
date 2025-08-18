# Simple PowerShell script to create test users
Write-Host "Creating LMS Test Users..." -ForegroundColor Green

$apiUrl = "http://localhost:8000/api/v1/auth"
$headers = @{"Content-Type" = "application/json"}

# Test creating teacher1
$teacherData = @{
    username = "teacher1"
    email = "teacher1@lms.local"
    password = "teacher123"
    full_name = "Teacher One"
    role = "teacher"
} | ConvertTo-Json

try {
    Write-Host "Creating teacher1..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "$apiUrl/register" -Method POST -Headers $headers -Body $teacherData
    Write-Host "SUCCESS: Created teacher1" -ForegroundColor Green
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test creating student1
$studentData = @{
    username = "student1"
    email = "student1@lms.local"
    password = "student123"
    full_name = "Student One"
    role = "student"
} | ConvertTo-Json

try {
    Write-Host "Creating student1..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "$apiUrl/register" -Method POST -Headers $headers -Body $studentData
    Write-Host "SUCCESS: Created student1" -ForegroundColor Green
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Done!" -ForegroundColor Cyan
