# GitHub Push Script
# Run this script after creating your GitHub repository

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,
    
    [Parameter(Mandatory=$false)]
    [string]$RepoName = "construction-bid-evaluator"
)

Write-Host "Setting up GitHub remote..." -ForegroundColor Green

# Add remote
$remoteUrl = "https://github.com/$GitHubUsername/$RepoName.git"
git remote add origin $remoteUrl

if ($LASTEXITCODE -eq 0) {
    Write-Host "Remote added successfully!" -ForegroundColor Green
} else {
    Write-Host "Remote might already exist, updating..." -ForegroundColor Yellow
    git remote set-url origin $remoteUrl
}

# Rename branch to main
git branch -M main

Write-Host "Pushing to GitHub..." -ForegroundColor Green
Write-Host "You may be prompted for GitHub credentials." -ForegroundColor Yellow

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "Repository URL: https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ Push failed. Common reasons:" -ForegroundColor Red
    Write-Host "1. Repository doesn't exist on GitHub - create it first at https://github.com/new" -ForegroundColor Yellow
    Write-Host "2. Authentication required - use GitHub Personal Access Token" -ForegroundColor Yellow
    Write-Host "3. Wrong repository URL - check your username and repo name" -ForegroundColor Yellow
}

