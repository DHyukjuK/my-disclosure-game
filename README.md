### How to connect a Google Sheet to the app

1. Create a Google Cloud project and enable the Google Sheets and Drive APIs.
2. Create a service account, and in the console create a JSON key for it. Download the JSON.
3. Create a Google Sheet to collect the data and copy the sheet ID from the sheet URL (the long ID in the URL after /d/).
4. Share the sheet with the service account's email address (e.g., my-service@project-id.iam.gserviceaccount.com) and give it Editor access.
5. Open your Streamlit app on Streamlit Cloud, go to Settings → Secrets and add these keys:

```
GSHEET_ID = "<your-google-sheet-id>"
GSHEETS_CREDENTIALS = { ... paste the JSON contents from your service account key ... }
ADMIN_KEY = "some-strong-password"
```

6. When deployed, click into the app, click the sidebar Admin login, enter the `ADMIN_KEY`, then you should see a successful Google Sheets connection and the option to download the sheet as CSV.

Security note: store the service account JSON in Streamlit Secrets (or environment variables on other hosting) and do not commit it to GitHub.

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

- The app writes participant responses to `disclosure_game_data.csv` on the server where the Streamlit app runs. This CSV does not automatically sync back to your GitHub repository.
- **To download collected data from a deployed app**: open the deployed Streamlit app, enable the sidebar `Admin mode` checkbox, and click the **Download collected data CSV** button — this downloads the runtime file the app has written. This is the simplest way to retrieve data from Streamlit Community Cloud.

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
	- **Google Sheets**: easiest to view & download; use `gspread` with a service account
	- **AWS S3** or **Google Cloud Storage**: for larger CSVs or file storage
- When deploying, store API keys and credentials safely in Streamlit Secrets (app settings on Streamlit Cloud) instead of committing them to GitHub.

If you want, I can implement Supabase or Google Sheets saving in the app and help set up the credentials.
## Google Sheets integration (recommended)

This app can optionally append every submitted row to a Google Sheet. This gives you a centrally stored CSV-like table that you can view, export, and analyze without connecting to the app server filesystem. Setup steps:

1. Create a Google Cloud project and enable the Google Sheets & Drive APIs.
2. Create a service account and a JSON key for that account.
3. Create a Google Sheet and share it with the service account email address (grant Editor permission).
4. Add the JSON key to your Streamlit app secrets under `GSHEETS_CREDENTIALS`. Streamlit Secrets supports nested JSON — you can paste the whole JSON object.
5. Add `GSHEET_ID` (the Google Sheet ID from the sheet URL) to Streamlit Secrets or as an environment variable.

Example secrets (Streamlit Cloud, `Settings → Secrets`):

```
GSHEETS_CREDENTIALS = { ... your service-account JSON object ... }
GSHEET_ID = "1abc...def"
```

With these secrets set, the app will append each saved submission to the first worksheet in the sheet. The admin UI allows downloading the sheet contents as a CSV.

Security & best practice:
- Do not commit keys to GitHub.
- Use `st.secrets` or environment variables for credentials.
- Limit who has the service account key and the sheet's sharing access.

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
