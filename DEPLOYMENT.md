# Deployment Guide - Streamlit Community Cloud

This guide walks you through deploying your Duty Roster Generator to Streamlit Community Cloud in 5 minutes, completely free.

## Prerequisites

- GitHub account (free)
- Google Account (for Gemini API)
- Project code on GitHub

## Step 1: Get Your Gemini API Key (2 minutes)

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Click **"Create API key in new Google Cloud project"**
5. Copy the generated API key
6. Keep it safe! You'll need it in Step 3

> **Free Tier Limits**: 15 requests/min, 1.5M tokens/day — Perfect for a few rosters per month

## Step 2: Push Code to GitHub (2 minutes)

### If you haven't initialized Git yet:

```bash
cd "Duty Roster Generator"
git init
git add .
git commit -m "Initial commit - Duty Roster Generator"
git remote add origin https://github.com/YOUR_USERNAME/duty-roster-generator.git
git branch -M main
git push -u origin main
```

### If you already have it on GitHub:

Just make sure latest changes are pushed:

```bash
git add .
git commit -m "Complete implementation"
git push
```

## Step 3: Deploy on Streamlit Cloud (1 minute)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"** (blue button)
3. Fill in the form:
   - **Repository**: `YOUR_USERNAME/duty-roster-generator`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Click **"Deploy"**

Streamlit will begin building your app. Wait 2-3 minutes...

## Step 4: Configure Secrets (1 minute)

Once your app is deployed:

1. Click the **gear icon** (⚙️) in the top right
2. Select **"Secrets"**
3. Paste your secrets (replace with your actual key):

```toml
GEMINI_API_KEY = "AIzaSyC..."
GEMINI_MODEL = "gemini-2.0-flash"
LOG_LEVEL = "INFO"
```

4. Click **"Save"** (app auto-reloads)

## Done! 🎉

Your app is now live at a unique URL like:
```
https://duty-roster-generator.streamlit.app
```

Share this link with your father! He can:
- Access it from any device (mobile, tablet, computer)
- No installation required
- Works in any modern browser

## Usage by End User

1. **Choose Template** → "Nursing Officer" or "Ward Boy/Aya"
2. **Upload Reference PDF** → Blank roster template
3. **Upload Photo** → Clear photo of handwritten roster
4. **Click Extract** → Gemini reads the handwriting
5. **Preview** → Review extracted data
6. **Generate PDF** → Creates final PDF
7. **Download** → One-click PDF download

## Updating Your App

After deployment, if you make changes:

```bash
git add .
git commit -m "Description of changes"
git push
```

Streamlit automatically detects the push and redeploys within minutes.

## Monitoring & Logs

In Streamlit Community Cloud dashboard:
- Click on your app
- View deployment status
- Check logs for errors
- Monitor resource usage

## Troubleshooting Deployment

### "Failed to build" error
- Check `requirements.txt` has all dependencies
- Ensure no syntax errors in Python files
- Verify template YAML files are valid

### "Gemini API key not configured"
- Go to app settings (⚙️) → Secrets
- Verify API key is correctly pasted
- No extra spaces or quotes

### App is slow or times out
- First image extraction takes ~10-15 seconds
- Subsequent images are faster
- If timeout: app may need more time, try again
- Streamlit free tier has limits but sufficient for a few uses/day

### "Template not found" error
- Ensure `templates/` folder is committed to GitHub
- Verify template YAML files are in repo
- Check template ID matches filename

## Scaling Up (When Needed)

If you need:
- Higher request limits
- More storage
- Custom domain
- Streamlit Community Cloud paid plans are available

But for a single user, free tier is perfect.

## Security Notes

- Never commit `.streamlit/secrets.toml` (it's in .gitignore)
- API key is only visible to you (not in GitHub)
- Streamlit Cloud keeps secrets encrypted
- PDFs are processed in-memory, not stored on server

## Local vs Cloud

### Local Testing
```bash
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
# Add your API key to secrets.toml
streamlit run app.py
```

### Streamlit Cloud
Add secrets via app settings — no local secrets needed

## Got Issues?

1. Check app logs (Streamlit dashboard)
2. Verify Gemini API quota (Google AI Studio)
3. Test with a clear, well-lit roster photo
4. Ensure PDF is single-page A4
5. Try refresh (Ctrl+Shift+R in browser)

## Next: Customization

Once deployed, you can:
- Add more templates (duplicate `nursing_officer.yaml`)
- Adjust PDF coordinates for your specific format
- Add email integration
- Create backup/archive system
- Add user authentication for teams

Enjoy your free Duty Roster Generator! 🏥📋✨
