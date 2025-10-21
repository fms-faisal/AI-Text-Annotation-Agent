#!/bin/bash

echo "🚀 Text Annotation Agent - Deployment Setup"
echo "==========================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: AI Text Annotation Agent"
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

echo ""
echo "📋 Next steps:"
echo ""
echo "1. Create a GitHub repository at https://github.com/new"
echo ""
echo "2. Run these commands:"
echo "   git remote add origin YOUR_GITHUB_REPO_URL"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Deploy to Render.com:"
echo "   - Go to https://render.com"
echo "   - Sign up/login"
echo "   - Click 'New +' → 'Web Service'"
echo "   - Connect your GitHub repository"
echo "   - Add environment variable: GEMINI_API_KEY"
echo "   - Click 'Create Web Service'"
echo ""
echo "4. Wait 5-10 minutes for deployment"
echo ""
echo "5. Share your live URL with others for feedback!"
echo ""
echo "📖 See DEPLOYMENT.md for detailed instructions"
echo ""
