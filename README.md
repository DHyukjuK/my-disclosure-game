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
- **Heroku**: Add a `Procfile` and deploy; see `Procfile` below.
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
