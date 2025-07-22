# 💰 Budget Deployment Guide

Choose your deployment strategy based on budget and needs:

## 🆓 Option 1: Railway.app (FREE - Recommended for beginners)

**Cost: $0/month (500 hours free, ~16 hours/day)**

### Step 1: Prepare Your Code
```bash
# Your app is already Railway-ready with the Procfile!
# Just make sure you commit all changes
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### Step 2: Deploy to Railway
1. Visit [railway.app](https://railway.app)
2. Click "Deploy from GitHub repo"
3. Authorize GitHub and select your repository
4. Railway will automatically:
   - Detect Python application
   - Install requirements.txt
   - Use the Procfile to start your app

### Step 3: Configure Environment Variables
In Railway dashboard, go to Variables and add:
```
FLASK_ENV=production
DATABASE_URL=sqlite:///data/climate_data.db
LOG_LEVEL=INFO
```

### Step 4: Access Your App
Railway will provide a URL like: `https://your-app-name.up.railway.app`

---

## 💸 Option 2: AWS Ultra-Budget (~$5/month)

**Cost: $3-7/month using smallest AWS instances**

### Quick Deploy
```bash
# Set your AWS credentials first
aws configure

# Set a secure database password
export DB_PASSWORD="YourSecurePassword123!"

# Deploy everything
./deploy-budget.sh
```

This creates:
- EC2 t4g.nano instance ($3.50/month)
- SQLite database (free)
- Nginx reverse proxy
- Automatic daily data updates

---

## 🆓 Option 3: Render.com (FREE with limitations)

**Cost: $0/month (spins down after inactivity)**

### Step 1: Create render.yaml
```yaml
# Already created for you!
services:
  - type: web
    name: climate-data-app
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py --env production --skip-processing
    envVars:
      - key: DATABASE_URL
        value: sqlite:///data/climate_data.db
```

### Step 2: Deploy
1. Push to GitHub
2. Visit [render.com](https://render.com)
3. Connect GitHub repository
4. Deploy automatically

---

## 🎯 Option 4: Hybrid Static (Ultra-cheap)

**Cost: $0-2/month for high-performance static site**

### Generate Static Version
```bash
# Create a static version that updates via GitHub Actions
python generate_static.py  # You'd need to create this

# Deploy to:
# - GitHub Pages (free)
# - Vercel (free)
# - Netlify (free)
```

---

## Cost Comparison

| Platform | Monthly Cost | Free Hours | Auto-scaling | Database |
|----------|-------------|-----------|---------------|----------|
| Railway.app | $0 | 500 hours | Yes | SQLite |
| Render.com | $0 | Always on* | Yes | SQLite |
| AWS Budget | $3-7 | Always on | No | SQLite |
| AWS Free Tier | $0** | 750 hours | Yes | RDS Free |
| GitHub Pages | $0 | Unlimited | No | Static only |

*Spins down after 15min inactivity  
**First 12 months only

## Recommended Path

### For Beginners → Railway.app
- Easiest setup
- Great free tier
- Automatic deployments
- Built-in monitoring

### For AWS Learners → AWS Free Tier
- Learn cloud architecture
- Free for 12 months
- Professional-grade setup
- Easy to scale later

### For Minimal Cost → EC2 Nano
- $3-5/month long-term
- Full control
- Always-on
- Good performance

## Quick Start Commands

### Railway Deploy
```bash
# 1. Push to GitHub
git push origin main

# 2. Go to railway.app and connect repo
# 3. Add environment variables
# 4. Deploy automatically
```

### AWS Budget Deploy  
```bash
export DB_PASSWORD="YourPassword123!"
./deploy-budget.sh
```

### Local Development
```bash
# Test locally first
docker-compose up
# Visit http://localhost:5000
```

Your app will be live and accessible to the world! 🌍