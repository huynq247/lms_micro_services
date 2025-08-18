# PowerShell script to create test users via API
# LMS Test Users Creation

Write-Host "🚀 Creating LMS Test Users..." -ForegroundColor Green

$apiUrl = "http://localhost:8000/api/v1/auth"
$headers = @{"Content-Type" = "application/json"}

# Test users data
$testUsers = @(
    @{username="teacher1"; email="teacher1@lms.local"; password="teacher123"; full_name="Nguyen Van Giao"; role="teacher"},
    @{username="teacher2"; email="teacher2@lms.local"; password="teacher456"; full_name="Tran Thi Huong"; role="teacher"},
    @{username="teacher3"; email="teacher3@lms.local"; password="teacher789"; full_name="Le Minh Tuan"; role="teacher"},
    @{username="student1"; email="student1@lms.local"; password="student123"; full_name="Pham Van An"; role="student"},
    @{username="student2"; email="student2@lms.local"; password="student456"; full_name="Ngo Thi Binh"; role="student"},
    @{username="student3"; email="student3@lms.local"; password="student789"; full_name="Hoang Minh Cuong"; role="student"},
    @{username="student4"; email="student4@lms.local"; password="student101"; full_name="Vu Thi Dung"; role="student"},
    @{username="student5"; email="student5@lms.local"; password="student202"; full_name="Dang Van Dinh"; role="student"}
)

$createdUsers = @()
$failedUsers = @()

foreach ($user in $testUsers) {
    $body = $user | ConvertTo-Json
    
    try {
        Write-Host "Creating user: $($user.username) ($($user.role))..." -ForegroundColor Yellow
        
        # Try to create user
        $response = Invoke-RestMethod -Uri "$apiUrl/register" -Method POST -Headers $headers -Body $body -ErrorAction Stop
        
        Write-Host "✅ Successfully created: $($user.username)" -ForegroundColor Green
        $createdUsers += $user
        
        # Test login
        $loginBody = @{
            username = $user.username
            password = $user.password
        } | ConvertTo-Json
        
        $loginResponse = Invoke-RestMethod -Uri "$apiUrl/login" -Method POST -Headers $headers -Body $loginBody -ErrorAction SilentlyContinue
        
        if ($loginResponse.access_token) {
            Write-Host "✅ Login test passed for: $($user.username)" -ForegroundColor Green
        }
        
    }
    catch {
        Write-Host "❌ Failed to create: $($user.username) - $($_.Exception.Message)" -ForegroundColor Red
        $failedUsers += $user
        
        # Try login in case user already exists
        try {
            $loginBody = @{
                username = $user.username
                password = $user.password
            } | ConvertTo-Json
            
            $loginResponse = Invoke-RestMethod -Uri "$apiUrl/login" -Method POST -Headers $headers -Body $loginBody -ErrorAction Stop
            
            if ($loginResponse.access_token) {
                Write-Host "ℹ️ User $($user.username) already exists and login works" -ForegroundColor Cyan
                $createdUsers += $user
            }
        }
        catch {
            Write-Host "❌ User $($user.username) does not exist or login failed" -ForegroundColor Red
        }
    }
    
    Start-Sleep -Milliseconds 500
}

Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "✅ Available users: $($createdUsers.Count)" -ForegroundColor Green
Write-Host "❌ Failed users: $($failedUsers.Count)" -ForegroundColor Red

if ($createdUsers.Count -gt 0) {
    Write-Host "`n🎉 You can now test with these accounts:" -ForegroundColor Green
    
    $teachers = $createdUsers | Where-Object { $_.role -eq "teacher" }
    $students = $createdUsers | Where-Object { $_.role -eq "student" }
    
    Write-Host "`n🧑‍🏫 Teachers ($($teachers.Count)):" -ForegroundColor Blue
    foreach ($teacher in $teachers) {
        Write-Host "  - $($teacher.username) / $($teacher.password) ($($teacher.full_name))" -ForegroundColor White
    }
    
    Write-Host "`n🎓 Students ($($students.Count)):" -ForegroundColor Magenta  
    foreach ($student in $students) {
        Write-Host "  - $($student.username) / $($student.password) ($($student.full_name))" -ForegroundColor White
    }
}

Write-Host "`n🌐 Frontend URL: http://localhost:3000/login" -ForegroundColor Yellow
Write-Host "🔗 API Gateway: http://localhost:8000" -ForegroundColor Yellow

Write-Host "`n🧪 Ready for testing!" -ForegroundColor Green
