### Data access and admin download

- The app saves participant responses to `disclosure_game_data.csv` on the server where the app runs. This CSV does not sync back to GitHub automatically.
- To download collected data from a deployed app: open the deployed Streamlit app, enter the `ADMIN_KEY` in the sidebar admin login, and click the **Download collected data CSV** button.

### Admin authentication

- Set the admin key in Streamlit Cloud under "Settings → Secrets":

```text
ADMIN_KEY = "your-strong-password"
```

- When running locally, set the `ADMIN_KEY` environment variable:

```powershell
$env:ADMIN_KEY = "your-strong-password"
```

# Disclosure Game

This repo contains a Streamlit-based Python app `disclosure_game.py` for the PSY360 final project.

## Run locally
1. Create and activate a virtual environment and install requirements:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the Streamlit app:

```powershell
streamlit run disclosure_game.py
```

## Import to GitHub (quick)
1. Initialize git and commit files

```bash
git init
git add .
git commit -m "Initial commit: disclosure game"
```

2. Create a new GitHub repository (via web UI or with GitHub CLI):

- Web: Create a new repo at https://github.com/new and follow instructions to add a remote.
- GitHub CLI (if installed/authorized):

```bash
gh repo create my-disclosure-game --public --source=. --push
```

If created manually on the web, add a remote and push:

```bash
git remote add origin https://github.com/your-username/your-repo.git
git branch -M main
git push -u origin main
```

## Deploy as a webpage (recommended: Streamlit Community Cloud)
1. Sign in to Streamlit Community Cloud (https://share.streamlit.io/) and connect your GitHub account.
2. Click "New app" and select the GitHub repository and branch. For `Main file path`, put `disclosure_game.py`.
3. Streamlit will automatically install dependencies from `requirements.txt` and build the app.

Other deployment options:

## Where submission data is saved

The app writes participant responses to `disclosure_game_data.csv` on the server where the Streamlit app runs. This CSV does not automatically sync back to your GitHub repository; use the admin-side download to retrieve stored data.

### Admin authentication

- The app now requires an admin key to access the CSV download. Set the admin key in Streamlit Cloud under "Settings → Secrets":

```
ADMIN_KEY = "your-strong-password"
```

- Alternatively, when running locally, set the `ADMIN_KEY` environment variable:

```bash
export ADMIN_KEY="your-strong-password"
# Windows (PowerShell)
$env:ADMIN_KEY = "your-strong-password"
```

- In the deployed app sidebar, enter the admin key and click "Log in as admin" to reveal the download button.

## Recommended long-term storage for data

 - Use an external database or hosted service so your data is always centrally stored and accessible:
	- **Supabase**: hosted Postgres with REST API and client libraries
	- **Google Sheets** or **Google Drive** (manual/import/export) for simple non-sensitive datasets
	- **AWS S3** or **Google Cloud Storage**: for larger CSVs or file storage
When deploying, store API keys and credentials safely in Streamlit Secrets (app settings on Streamlit Cloud) instead of committing them to GitHub.

If you want, I can implement Supabase saving in the app and help set up the credentials.
## External storage options (optional)

If you prefer central storage instead of server CSVs, you can use external storage like Supabase (Postgres), Google Drive/Sheets (manual export), or AWS S3. I can help set this up if you want.

Other hosting options:
 - **Render**: Create a Web Service, specify build & start commands.
- **Vercel**: Not ideal for Streamlit; prefer Render or Heroku.

## Heroku Deployment (optional)
Create a Heroku app and push code. Use the following `Procfile` so Heroku can run Streamlit:

```
web: streamlit run disclosure_game.py --server.port $PORT --server.address 0.0.0.0
```

Then use the Heroku CLI:

```bash
heroku login
heroku create my-disclosure-game
git push heroku main
```

## Notes
- Streamlit Community Cloud is the easiest way to host Streamlit apps and is free for public repositories.
- Ensure `requirements.txt` contains `streamlit` and other dependencies used by the app.
