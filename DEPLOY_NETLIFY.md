# Deploy SwaraGuard on Netlify (Free Public Link)

## Step 1: Push your code to GitHub

```bash
cd "/Users/saradhi/untitled folder1/SwaraGuard"
git init
git add .
git commit -m "SwaraGuard hackathon project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/swaraguard.git
git push -u origin main
```

## Step 2: Connect to Netlify

1. Go to https://app.netlify.com
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect your GitHub account
4. Select your `swaraguard` repository
5. Click **"Deploy site"**

## Step 3: Customize your site name (optional)

1. In Netlify dashboard → **Site configuration** → **Site details**
2. Change site name to `deepfake-scam-protection`
3. Your live link will be: `https://deepfake-scam-protection.netlify.app/`

## Alternative: Deploy via Netlify Drop (drag & drop)

1. Go to https://app.netlify.com/drop
2. Drag the `web-designs/` folder and drop it
3. Your site goes live instantly

## What gets published

| File | Purpose |
|------|---------|
| `page1_home.html` | Homepage with "Protect Your Voice, Protect Your Money" |
| `page2_analysis.html` | AI analysis page |
| `page3_protection.html` | Protection flow page |
| `netlify.toml` | Netlify config (redirects + headers) |

## Update this file

Edit `HACKATHON_DOCS.md` and replace the live demo link with your actual Netlify URL once deployed.

```
Live Demo: https://deepfake-scam-protection.netlify.app/
```