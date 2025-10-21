# Deployment Guide

## Option 1: Render.com (Recommended - Free)

### Steps:

1. **Push to GitHub:**

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to https://render.com and sign up
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` configuration
   - Add environment variable: `GEMINI_API_KEY` (your API key)
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Your app will be live at: `https://your-app-name.onrender.com`

### Free Tier Limits:

- 750 hours/month
- Auto-sleeps after 15 min of inactivity
- Takes ~30 seconds to wake up

---

## Option 2: Railway.app (Alternative)

### Steps:

1. **Push to GitHub** (same as above)

2. **Deploy on Railway:**
   - Go to https://railway.app and sign up
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Add environment variable: `GEMINI_API_KEY`
   - Railway auto-detects Python and installs dependencies
   - Set start command: `cd backend && gunicorn app:app`
   - Your app will be live at: `https://your-app.up.railway.app`

### Free Tier:

- $5 credit/month (resets monthly)
- ~500 hours of usage

---

## Option 3: Vercel (Alternative - Good for Static + API)

### Steps:

1. **Push to GitHub** (same as above)

2. **Deploy on Vercel:**
   - Go to https://vercel.com and sign up
   - Click "New Project"
   - Import your GitHub repository
   - Configure:
     - Framework Preset: Other
     - Build Command: `cd backend && pip install -r requirements.txt`
     - Output Directory: `backend`
   - Add environment variable: `GEMINI_API_KEY`
   - Deploy

### Free Tier:

- Unlimited bandwidth
- 100GB bandwidth/month
- Serverless functions included

---

## Option 4: PythonAnywhere (Quick & Simple)

### Steps:

1. Sign up at https://www.pythonanywhere.com (free tier)
2. Upload your code via Files tab
3. Install dependencies in Bash console:
   ```bash
   pip install --user -r requirements.txt
   ```
4. Configure Web app:
   - Python version: 3.10
   - Source code: `/home/username/text-annotation-agent/backend`
   - WSGI file: Point to `app.py`
5. Add environment variable in Web tab
6. Reload app

### Free Tier:

- yourname.pythonanywhere.com subdomain
- Limited CPU/RAM
- Always on (doesn't sleep)

---

## Testing Your Deployment

After deploying, test these endpoints:

- `GET /` - Main UI
- `GET /api/health` - Health check
- `POST /api/annotate` - Annotation endpoint
- `POST /api/chat` - Chat endpoint

---

## Sharing with Others

Once deployed, share your URL:

- **Render**: `https://text-annotation-agent.onrender.com`
- **Railway**: `https://text-annotation-agent.up.railway.app`
- **PythonAnywhere**: `https://yourusername.pythonanywhere.com`

### Get Feedback:

- Share on Twitter/LinkedIn with the URL
- Create a feedback form (Google Forms)
- Add analytics (Google Analytics)
- Monitor usage in platform dashboard

---

## Important Notes

⚠️ **Security:**

- Never commit `.env` file to GitHub
- Keep your `GEMINI_API_KEY` in environment variables
- Consider adding rate limiting for production

💡 **Free Tier Limitations:**

- **Render**: Sleeps after 15 min inactivity (30s wake time)
- **Railway**: $5 monthly credit limit (~500 hours)
- **Vercel**: Serverless function time limits
- **PythonAnywhere**: CPU and RAM restrictions

🎯 **Best for Feedback:**

- **Render**: Best for demos and quick sharing (free, auto-deploy, auto-wake)
- **Railway**: Best for active testing (no sleep, fast performance)
- **Vercel**: Best for API-heavy apps (serverless, scalable)
- **PythonAnywhere**: Best for 24/7 availability (always on)

---

## ⚠️ Note About Heroku

**Heroku no longer offers a free tier** as of November 2022. All Heroku plans now require payment. Consider the free alternatives listed above instead.
