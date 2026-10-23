for ($i=1; $i -le 6; $i++) {
    Write-Host "Request $i"
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/completions" -Method Post -ContentType "application/json" -Headers @{"x-api-key"="choose-a-random-secret-string-here"} -Body '{"prompt": "test", "max_tokens": 5}'
    } catch {
        Write-Host "Error: $($_.Exception.Message)"
    }
}