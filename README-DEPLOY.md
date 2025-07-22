# 🚂 Railway.app Deployment Guide

Deploy your Climate Data Analysis app to Railway.app for **FREE**!

## Why Railway.app?
- **$0/month** for hobby projects (500 hours free)
- **Zero configuration** - just connect GitHub
- **Automatic deployments** from your repository
- **Built-in monitoring** and logging
- **Custom domains** available
- **Scales automatically** if needed

## Quick Deploy (5 minutes)

### Step 1: Prepare Your Repository
Your code is already Railway-ready! Just make sure everything is committed:

```bash
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### Step 2: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Click **"Deploy from GitHub repo"**
3. Sign in with GitHub and authorize Railway
4. Select your **GHCNV4_Analysis** repository
5. Railway will automatically detect it's a Python app and start deploying

### Step 3: Configure Environment Variables
After deployment starts, go to your project dashboard and add these variables:

**Click Variables → Add Variable:**
```
FLASK_ENV=production
DATABASE_URL=sqlite:///data/climate_data.db
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here-change-this
```

### Step 4: Wait for Deployment
Railway will:
- Install Python dependencies from `requirements.txt`
- Use the `Procfile` to start your app
- Run the database verification
- Provide you with a public URL

### Step 5: Access Your App
Railway will give you a URL like:
```
https://ghcnv4analysis-production.up.railway.app
```

## Your App Features on Railway

✅ **Automatic Data Processing**: Runs when the app starts  
✅ **Interactive Charts**: All your Phase 2 features work  
✅ **Dark/Light Mode**: System preference detection  
✅ **Data Export**: CSV and PNG downloads  
✅ **Trend Analysis**: Linear regression and moving averages  
✅ **Advanced Statistics**: Correlation analysis  

## Cost Breakdown

- **Railway.app**: $0/month (500 hours = ~16 hours/day)
- **Database**: SQLite (included, no extra cost)
- **Storage**: Included in Railway's free tier
- **Bandwidth**: Included in Railway's free tier

**Total: $0/month** 🎉

## Managing Your Deployment

### View Logs
```bash
# In Railway dashboard, go to "Deployments" → "View Logs"
# Or use Railway CLI:
railway logs
```

### Redeploy
```bash
# Just push to GitHub - Railway auto-deploys
git push origin main
```

### Update Data
Your app automatically processes data on startup, but you can also trigger it manually through the web interface or by redeploying.

### Custom Domain (Optional)
1. In Railway dashboard, go to "Settings"
2. Add your custom domain
3. Update your DNS to point to Railway

## Local Development

Test locally before deploying:
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py

# Or with Docker
docker-compose up
```

## Troubleshooting

### App won't start?
1. Check logs in Railway dashboard
2. Verify environment variables are set
3. Make sure `requirements.txt` is committed

### Database issues?
1. Railway uses SQLite by default (no setup needed)
2. Data persists between deployments
3. Check logs for any database errors

### Out of free hours?
- Railway gives 500 hours/month free
- That's about 16 hours per day
- For 24/7 uptime, upgrade to hobby plan ($5/month)

## Next Steps

Once deployed:
1. **Share your app** - it's live on the internet!
2. **Monitor usage** in Railway dashboard
3. **Set up custom domain** if desired
4. **Consider upgrading** if you need more resources

Your climate data analysis app is now live and accessible to anyone! 🌍

## Need Help?

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: Great community support
- **GitHub Issues**: Report problems in your repository

Happy deploying! 🚀