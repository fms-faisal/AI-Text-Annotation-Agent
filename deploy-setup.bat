@echo off
echo.
echo ========================================
echo   Text Annotation Agent - Setup
echo ========================================
echo.

REM Check if git is initialized
if not exist ".git" (
    echo Initializing git repository...
    git init
    git add .
    git commit -m "Initial commit: AI Text Annotation Agent"
    echo Git initialized!
) else (
    echo Git already initialized!
)

echo.
echo ========================================
echo   DEPLOYMENT STEPS
echo ========================================
echo.
echo 1. Create GitHub repository:
echo    Go to: https://github.com/new
echo.
echo 2. Connect your repo:
echo    git remote add origin YOUR_GITHUB_REPO_URL
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. Deploy to Render.com (FREE):
echo    - Visit: https://render.com
echo    - Sign up and login
echo    - Click "New +" then "Web Service"
echo    - Connect your GitHub repository
echo    - Add environment variable:
echo      Name: GEMINI_API_KEY
echo      Value: [your API key]
echo    - Click "Create Web Service"
echo.
echo 4. Wait 5-10 minutes for deployment
echo.
echo 5. Share your live URL for feedback!
echo.
echo See DEPLOYMENT.md for more options
echo.
pause
