### Data access, backups, and admin download

- The app saves participant responses to `disclosure_game_data.csv` on the server where the app runs. This CSV does not sync back to GitHub automatically, but the app includes optional local timestamped backups and an admin-only CSV export.
- To download collected data from a deployed app: open the deployed Streamlit app, enter the `ADMIN_KEY` in the sidebar admin login, and click the **Download collected data CSV** button.
- The app supports automatic local backups on submission and a manual "Create local backup now" admin button. Backups are stored in `backups/` by default as `disclosure_game_data_YYYYMMDD_HHMMSS.csv`.

**Environment / Streamlit Secrets**

- `ADMIN_KEY` (required for admin): set this in Streamlit Cloud or as an environment variable to allow admin logins and CSV export.
- Default backup behavior: set these in Streamlit Secrets or environment variables (optional):

```text
BACKUP_ON_SUBMIT = "true"        # default is "true"
BACKUP_KEEP_LAST = "10"          # default is "10"
BACKUP_DIR = "backups"           # default: backups/
```

You can either enable/disable backups with `BACKUP_ON_SUBMIT`, or from the deployed app sidebar using the admin toggle. Manual backups are always available to admins using the "Create local backup now" button.


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

### Admin Data Viewer

- The app includes an admin-only Data Viewer in the sidebar (requires `ADMIN_KEY`).
- To view and download all collected submissions from the deployed app: sign into the app with admin key → open the sidebar → expand "View and download all submissions". You can download the CSV or preview submissions in a table.

### Optional: Persistent storage with Supabase

- If you want your data to persist across redeploys and server restarts, add a Supabase project and set these secrets in Streamlit:

```text
SUPABASE_URL = "https://<your>.supabase.co"
SUPABASE_KEY = "<service-role-or-anon-key>"
SUPABASE_TABLE = "disclosure_game"
```

The app will write submissions to the Supabase table in addition to the local CSV (if configured). Admins can download all rows from Supabase in the Data Viewer.

**Security note:** You can use an anonymous public key for writes if your table allows inserts, but the recommended approach is to create a Service Role key and keep it secret in Streamlit Secrets. When using Service Role keys, be extra careful to secure those secrets.

### Supabase table schema

When creating the table in Supabase, you can use this basic SQL schema so the columns match the CSV headers used by the app:

```sql
CREATE TABLE IF NOT EXISTS disclosure_game (
	timestamp text,
	netid text,
	timing_condition text,
	reciprocity_condition text,
	turn integer,
	participant_depth integer,
	partner_depth integer,
	partner_message text,
	trust integer,
	closeness integer,
	comfort integer,
	warmth integer,
	perceived_openness integer,
	reciprocity_rating integer,
	enjoyment integer,
	strategy_adjustment integer,
	strategy_text text
);
```

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
