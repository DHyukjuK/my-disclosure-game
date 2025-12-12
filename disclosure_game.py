import streamlit as st
import random
import csv
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import io
import os
import traceback
from typing import Dict, Any

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="Self-Disclosure Game", page_icon="💬")

# ----------------- DATA FILE SETUP -----------------
DATA_FILE = Path(os.getenv("DATA_FILE_PATH", "disclosure_game_data.csv"))
TRIGGER_FILE = Path(os.getenv("TRIGGER_FILE_PATH", ".submission_trigger"))

# Consistent header for the CSV file
CSV_HEADERS = [
    "timestamp",
    "netid",
    "timing_condition",
    "reciprocity_condition",
    "turn",
    "participant_depth",
    "partner_depth",
    "partner_message",
    "trust",
    "closeness",
    "comfort",
    "warmth",
    "perceived_openness",
    "reciprocity_rating",
    "enjoyment",
    "strategy_adjustment",
    "strategy_text",
]
# App stores data in a local CSV on the server; admin can download it.

# If the CSV file doesn't exist yet, create it with a header row
if not DATA_FILE.exists():
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)

# ----------------- OPTIONAL: GITHUB BACKUP (NO ACCOUNT REQUIRED UNLESS YOU WANT IT) -----------------
GITHUB_TOKEN = None
GITHUB_REPO = None
GITHUB_BRANCH = None
GITHUB_PATH = None
try:
    GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")
    GITHUB_REPO = st.secrets.get("GITHUB_REPO") or os.getenv("GITHUB_REPO")
    GITHUB_BRANCH = st.secrets.get("GITHUB_BRANCH") or os.getenv("GITHUB_BRANCH", "main")
    GITHUB_PATH = st.secrets.get("GITHUB_PATH") or os.getenv("GITHUB_PATH", "disclosure_game_data.csv")
except Exception:
    GITHUB_TOKEN = None
    GITHUB_REPO = None
    GITHUB_BRANCH = None
    GITHUB_PATH = None


def push_csv_to_github(csv_bytes: bytes) -> bool:
    """Push the CSV bytes to the configured repo path using GITHUB_TOKEN.
    If no credentials are set, this is a no-op that returns False.
    This avoids requiring external accounts unless you explicitly set a token.
    """
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return False
    import base64
    import json
    import requests

    try:
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
        # Get current file sha if exists
        get_resp = requests.get(api_url + f"?ref={GITHUB_BRANCH}", headers=headers)
        if get_resp.status_code == 200:
            sha = get_resp.json().get("sha")
        else:
            sha = None
        content_b64 = base64.b64encode(csv_bytes).decode("utf-8")
        payload = {
            "message": "Automated CSV backup from Streamlit app",
            "content": content_b64,
            "branch": GITHUB_BRANCH,
        }
        if sha:
            payload["sha"] = sha
        put_resp = requests.put(api_url, headers=headers, data=json.dumps(payload))
        return put_resp.status_code in (201, 200)
    except Exception:
        return False

# ----------------- PARTNER OPENING MESSAGES -----------------
# Openers depend on timing (early/gradual) and reciprocity style.
# Each entry has a starting depth (0 or 1) and a list of possible messages.
PARTNER_OPENINGS = {
    "early": {
        "reciprocal": {
            "depth": 1,  # shallow
            "messages": [
                "Hey, nice to meet you. This week has been busy with classes, but I actually like meeting new people.",
                "Hi! I’ve been running around with school stuff, but it’s nice to take a break and talk to someone.",
            ],
        },
        "guarded": {
            "depth": 0,  # very surface level
            "messages": [
                "Hey, nice to meet you. I’ve mostly just been going to class and trying to stay on top of things.",
                "Hi! Nothing too exciting here—just the usual lectures and problem sets.",
            ],
        },
    },
    "gradual": {
        "reciprocal": {
            "depth": 0,
            "messages": [
                "Hey, nice to meet you. I’m usually a little quiet at first but I warm up once I get talking to someone.",
                "Hi! I can be a bit shy early on, but I do enjoy getting to know people gradually.",
            ],
        },
        "guarded": {
            "depth": 0,
            "messages": [
                "Hi, nice to meet you. I’m generally more of a listener than a talker when I first meet someone.",
                "Hey. I don’t usually share a lot about myself right away, but I’m fine chatting a bit.",
            ],
        },
    },
}

# ----------------- PARTNER CONTENT MESSAGES -----------------
# Pure content by depth: 0 = surface, 1 = a bit personal, 2 = more vulnerable.
PARTNER_CONTENT = {
    0: [
        "I’ve mostly just been bouncing between classes and the dining hall lately.",
        "My days have been pretty routine—class, homework, and trying not to fall asleep in lectures.",
        "Nothing too wild going on, just a lot of readings and assignments to get through.",
        "I spend a lot of time scrolling on my phone between things instead of doing anything interesting.",
    ],
    1: [
        "Outside of work, I like watching shows and going on walks when the weather isn’t awful.",
        "When I get a break, I usually end up hanging out with friends or playing games in someone’s room.",
        "I really like finding new music and making playlists—it’s kind of my default hobby.",
        "I try to go to the gym a couple times a week, but I’m not always consistent about it.",
        "I’m studying subjects that are pretty intense, so I really value the little relaxing moments I get.",
    ],
    2: [
        "I’ve had times here where I’ve felt really overwhelmed and worried I wouldn’t be able to keep up.",
        "Sometimes I feel like everyone else has things figured out and I’m just faking it.",
        "I’ve gone through stretches where I felt pretty isolated, even though I was surrounded by people.",
        "Balancing expectations from family with what I actually want has been really stressful at times.",
        "There have been moments where I seriously questioned whether I belong here as much as other people.",
        "I’m still figuring out how to talk about stress and mental health without feeling like I’m a burden.",
    ],
}

# ----------------- SESSION STATE INIT -----------------
if "initialized" not in st.session_state:
    st.session_state.initialized = False

if "used_partner_messages" not in st.session_state:
    st.session_state.used_partner_messages = set()  # to avoid exact repeats


# ----------------- HELPER FUNCTIONS -----------------
def depth_to_label(depth: int) -> str:
    """Human-readable description of a depth level (no numbers shown to participant)."""
    return {
        0: "kept things very surface-level",
        1: "shared a little personal information",
        2: "shared something pretty personal or vulnerable",
    }[depth]


def choose_unique_message(candidates):
    """Choose a message from candidates, avoiding exact repeats within this conversation."""
    used = st.session_state.used_partner_messages
    fresh = [m for m in candidates if m not in used]
    if fresh:
        msg = random.choice(fresh)
    else:
        msg = random.choice(candidates)
    used.add(msg)
    st.session_state.used_partner_messages = used
    return msg


def choose_opening_message(timing: str, reciprocity: str):
    """Pick opening depth and message based on condition."""
    info = PARTNER_OPENINGS[timing][reciprocity]
    depth = info["depth"]  # 0 or 1
    message = choose_unique_message(info["messages"])
    return depth, message


def build_partner_message(partner_depth: int) -> str:
    """
    Build a partner message for a given depth.
    No explicit talk about matching; just content that reflects how open they’re being.
    """
    return choose_unique_message(PARTNER_CONTENT[partner_depth])





def init_game():
    """Initialize a new game for this participant, with partner starting first."""
    # Randomly assign condition: (timing, reciprocity)
    timing, reciprocity = random.choice([
        ("early", "reciprocal"),
        ("early", "guarded"),
        ("gradual", "reciprocal"),
        ("gradual", "guarded"),
    ])
    st.session_state.timing = timing
    st.session_state.reciprocity = reciprocity

    # Reset state
    st.session_state.turn = 1  # participant turns: 1..N
    st.session_state.history = []  # list of dicts per turn
    st.session_state.finished = False
    st.session_state.initialized = True
    st.session_state.used_partner_messages = set()

    # Partner opening move (always shallow or less; never deep)
    opening_depth, opening_message = choose_opening_message(timing, reciprocity)
    st.session_state.opening_depth = opening_depth
    st.session_state.opening_message = opening_message


def partner_policy(turn_idx, last_participant_depth, timing, reciprocity):
    """
    Decide partner disclosure depth (0/1/2) for the reply to a participant choice.

    Design:
    - Partner starts low (opening is 0 or 1).
    - Over turns, base depth gradually increases.
    - In the reciprocal condition, depth leans toward the participant's depth.
    - In the guarded condition, depth stays mostly shallow even if participant goes deep.
    """

    # Base depth by turn & timing: early vs gradual
    # 0 = very surface-level, 1 = a bit personal, 2 = deep / vulnerable
    if timing == "early":
        # Early partner warms up faster
        if turn_idx <= 2:
            base_depth = 1
        elif turn_idx <= 4:
            base_depth = 1
        else:
            base_depth = 2
    else:  # gradual
        # Gradual partner stays lower for longer
        if turn_idx <= 2:
            base_depth = 0
        elif turn_idx <= 4:
            base_depth = 1
        else:
            base_depth = 2

    if reciprocity == "reciprocal":
        # Move toward participant depth with some "weight" on each
        combined = round(0.4 * base_depth + 0.6 * last_participant_depth)
        depth = combined
    else:  # guarded
        # Mostly limited to shallow, even if base or participant is deep
        depth = min(base_depth, 1)

    # Clamp to [0, 2]
    depth = int(max(0, min(depth, 2)))
    return depth

# ----------------- PAGE UI -----------------
st.title("Self-Disclosure Conversation Game 💬")

st.markdown(
    "You’ll see a short sequence of messages from a **simulated conversation partner** (assume you are talking to this person for the first time).\n\n"
    "After each partner message, imagine how you would respond in a real chat. "
    "Instead of typing a message, you’ll simply choose **how personal** your response would be.\n\n"
    "Think of the options like this:\n"
    "- **Keep it very surface-level:** you wouldn’t really share personal info (just small talk).\n"
    "- **Share something a little personal:** you might mention a hobby, class, or everyday detail about yourself.\n"
    "- **Share something pretty personal or vulnerable:** you might talk about feelings, worries, or deeper experiences.\n\n"
    "There are no right or wrong answers — just pick whatever best matches how you *would* respond."
)

netid = st.text_input("Your name or NetID (e.g., ab1234):", "")

# ----------------- ADMIN DOWNLOAD MODE -----------------
# Use the sidebar to reveal a simple admin-only CSV download for the file that
# lives on the deployed server (this does NOT push the CSV to GitHub).
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

# Admin key: read from Streamlit secrets first, then environment variable.
ADMIN_KEY = None
try:
    ADMIN_KEY = st.secrets["ADMIN_KEY"]
except Exception:
    ADMIN_KEY = os.getenv("ADMIN_KEY")

# Admin login UI
if not st.session_state.admin_authenticated:
    entered_key = st.sidebar.text_input("Admin key", type="password")
    if st.sidebar.button("Log in as admin"):
        if ADMIN_KEY and entered_key == ADMIN_KEY:
            st.session_state.admin_authenticated = True
            st.sidebar.success("Admin login successful.")
        else:
            st.sidebar.error("Invalid admin key.")
else:
    if st.sidebar.button("Log out of admin mode"):
        st.session_state.admin_authenticated = False

if st.session_state.admin_authenticated:
    # Admin option: automatically show download button when new submissions arrive
    if "admin_auto_show_on_new" not in st.session_state:
        st.session_state.admin_auto_show_on_new = True
    st.session_state.admin_auto_show_on_new = st.sidebar.checkbox(
        "Auto-show download on new submissions",
        value=st.session_state.admin_auto_show_on_new,
    )
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "rb") as f:
                csv_bytes = f.read()
            st.sidebar.download_button(
                label="Download collected data CSV",
                data=csv_bytes,
                file_name="disclosure_game_data.csv",
                mime="text/csv",
            )
            # No Google Sheets: admin-only download serves the local CSV only
            st.sidebar.info("This file contains the data saved on the deployed app instance.")
        except Exception as e:
            st.sidebar.error(f"Error reading data file: {e}")
        else:
            st.sidebar.info("No data file yet (no submissions recorded).")
    # Data is stored locally on the server for admin download
    total_rows = 0
    try:
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                total_rows = sum(1 for _ in f) - 1  # subtract header
    except Exception:
        total_rows = 0
    st.sidebar.info(f"Submissions saved on server: {max(total_rows,0)}")

    # Show a small notice if a new submission has arrived since admin last checked
    try:
        if TRIGGER_FILE.exists():
            last_trigger = TRIGGER_FILE.stat().st_mtime
        else:
            last_trigger = 0
        last_seen_key = "admin_last_seen_trigger"
        if last_seen_key not in st.session_state:
            st.session_state[last_seen_key] = 0
        if last_trigger > st.session_state[last_seen_key]:
            if st.session_state.admin_auto_show_on_new:
                st.sidebar.success("New submissions available — use the download button below.")
            st.session_state[last_seen_key] = last_trigger
    except Exception:
        pass

    # Admin-only preview: show the last 10 submissions (no pandas required)
    try:
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as _f:
                reader = csv.DictReader(_f)
                rows = list(reader)
            if rows:
                st.sidebar.subheader("Recent submissions (last 10)")
                st.sidebar.dataframe(rows[-10:])
    except Exception:
        pass

    # Admin data viewer: show a full table and download button
    with st.sidebar.expander("View and download all submissions"):
        try:
            # Read from local CSV by default (no pandas required)
            if DATA_FILE.exists():
                with open(DATA_FILE, "r", encoding="utf-8") as _f:
                    reader = csv.DictReader(_f)
                    rows = list(reader)
            else:
                rows = []

            st.write(f"Total submissions: {len(rows)}")
            st.dataframe(rows)
            # Convert rows (list of dicts) to CSV bytes
            import io as _io
            if rows:
                buf = _io.StringIO()
                w = csv.DictWriter(buf, fieldnames=CSV_HEADERS)
                w.writeheader()
                w.writerows(rows)
                csv_bytes_all = buf.getvalue().encode("utf-8")
            else:
                csv_bytes_all = b""
            st.download_button(
                label="Download full CSV",
                data=csv_bytes_all,
                file_name="disclosure_game_all_submissions.csv",
                mime="text/csv",
            )
        except Exception:
            # If pandas or remote store isn't available, provide the basic CSV download
            if DATA_FILE.exists():
                try:
                    with open(DATA_FILE, "rb") as _f:
                        _csv_bytes = _f.read()
                    st.download_button(
                        label="Download CSV file",
                        data=_csv_bytes,
                        file_name="disclosure_game_data.csv",
                        mime="text/csv",
                    )
                except Exception:
                    st.warning("Unable to load the data for viewing or download.")

if not st.session_state.initialized:
    if st.button("Start conversation"):
        if netid.strip():
            st.session_state.netid = netid.strip()
            init_game()
        else:
            st.warning("Please enter your name or NetID before starting.")

# ----------------- SHOW CONVERSATION (ALWAYS, EVEN AFTER FINISH) -----------------
if st.session_state.initialized:

    st.subheader("Conversation")

    total_turns = 6
    # For the progress bar, if finished, show 100%
    if st.session_state.finished:
        progress_fraction = 1.0
    else:
        progress_fraction = (st.session_state.turn - 1) / total_turns
    st.progress(progress_fraction)

    # Opening partner message
    st.markdown(f"**Conversation Partner (Opening):** {st.session_state.opening_message}")

    # Show full conversation history so far
    for entry in st.session_state.history:
        turn = entry["turn"]
        p_depth = entry["participant_depth"]
        partner_message = entry["partner_message"]

        st.markdown(
            f"**You (Turn {turn}):** You would have {depth_to_label(p_depth)} in your reply."
        )
        st.markdown(f"**Conversation Partner:** {partner_message}")

# ----------------- CONVERSATION LOOP (CHOICE PHASE) -----------------
if st.session_state.initialized and not st.session_state.finished:

    current_turn = st.session_state.turn
    total_turns = 6

    if current_turn <= total_turns:
        st.markdown(f"### Your turn (Turn {current_turn} of {total_turns})")

        # Depth options as natural language (no numbers shown)
        depth_labels = [
            "I would keep it very surface-level and not share anything personal.",
            "I would share something a little personal, but not very deep.",
            "I would share something pretty personal or vulnerable.",
        ]
        label_to_depth = {
            depth_labels[0]: 0,
            depth_labels[1]: 1,
            depth_labels[2]: 2,
        }

        choice_label = st.radio(
            "If you were replying to your partner right now, how personal would you be?",
            depth_labels,
            index=None,
            key=f"choice_{current_turn}",
        )

        if st.button("Submit choice", key=f"send_{current_turn}"):
            if choice_label is None:
                st.warning("Please choose one of the options before continuing.")
            else:
                participant_depth = label_to_depth[choice_label]

                # Decide partner's next depth based on policy
                timing = st.session_state.timing
                reciprocity = st.session_state.reciprocity
                partner_depth = partner_policy(
                    current_turn,
                    participant_depth,
                    timing,
                    reciprocity,
                )

                # Build partner's message at that depth
                partner_message = build_partner_message(partner_depth)

                # Record this turn
                st.session_state.history.append({
                    "turn": current_turn,
                    "participant_depth": participant_depth,
                    "partner_depth": partner_depth,
                    "partner_message": partner_message,
                })

                # Advance to next turn or mark finished
                st.session_state.turn += 1
                if st.session_state.turn > total_turns:
                    st.session_state.finished = True

# ----------------- POST-CONVERSATION QUESTIONS -----------------
if st.session_state.initialized and st.session_state.finished:
    st.subheader("Post-conversation questions")

    st.markdown(
        "You can refer back to the conversation above while answering these questions."
    )

    trust = st.slider("How much did you feel you could trust your partner?", 1, 7, 4)
    closeness = st.slider("How close or connected did you feel to your partner?", 1, 7, 4)
    comfort = st.slider("How comfortable did you feel during the interaction?", 1, 7, 4)
    warmth = st.slider("How warm and friendly did your partner seem?", 1, 7, 4)
    perceived_openness = st.slider("How open was your partner overall?", 1, 7, 4)
    reciprocity_rating = st.slider("How much did your partner seem to match your level of depth?", 1, 7, 4)
    enjoyment = st.slider("How engaging or enjoyable was this interaction overall?", 1, 7, 4)
    strategy_adjustment = st.slider(
        "How much did you adjust your depth based on how your partner behaved?",
        1, 7, 4,
    )
    strategy_text = st.text_area(
        "In one or two sentences, how would you describe your strategy in this conversation? (Optional)",
        value="",
        key="strategy_text",
    )

    if st.button("Submit and save data"):
        timestamp = datetime.utcnow().isoformat()
        netid_value = st.session_state.netid
        timing = st.session_state.timing
        reciprocity = st.session_state.reciprocity

        try:
            with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                _rows_for_supabase = []
                for entry in st.session_state.history:
                    row = [
                        timestamp,
                        netid_value,
                        timing,
                        reciprocity,
                        entry["turn"],
                        entry["participant_depth"],
                        entry["partner_depth"],
                        entry["partner_message"],
                        trust,
                        closeness,
                        comfort,
                        warmth,
                        perceived_openness,
                        reciprocity_rating,
                        enjoyment,
                        strategy_adjustment,
                        strategy_text,
                    ]
                    writer.writerow(row)
                    # Append to list for optional Supabase insert
                    _rows_for_supabase.append({CSV_HEADERS[i]: row[i] for i in range(len(CSV_HEADERS))})
                # If Supabase configured, insert these rows remotely too
                # If a GitHub token + repo is configured, back up CSV to GitHub
                try:
                    with open(DATA_FILE, "rb") as _backup_f:
                        _csv_bytes_local = _backup_f.read()
                    if GITHUB_TOKEN and GITHUB_REPO:
                        pushed = push_csv_to_github(_csv_bytes_local)
                        if pushed:
                            st.info("CSV backed up to GitHub repository")
                except Exception:
                    # Non-fatal: backups are best-effort
                    pass
                # Touch the trigger file so admin sessions see new submissions.
                try:
                    TRIGGER_FILE.write_text(datetime.utcnow().isoformat())
                except Exception:
                    pass
        except Exception as e:
            st.error("Unable to save data on the server. The file system may be read-only or there was another error.")
            st.exception(e)
            st.markdown("If you repeatedly see this error on the deployed app, consider using a remote database or set the `DATA_FILE_PATH` environment variable to a writable location.")
            # Debug print trace to server logs for deploy troubleshooting
            traceback.print_exc()
            # Do not try to continue; leave state as-is so a retry won't lose data
            raise

        st.success("Thanks! Your responses have been recorded.")
        st.markdown(
            "Note: The conversation partner in this interaction was scripted as part of a research study "
            "on how people time self-disclosure."
        )

        # Reset everything for a future participant
        st.session_state.initialized = False
        st.session_state.finished = False
        st.session_state.history = []
        st.session_state.turn = 1
        st.session_state.used_partner_messages = set()

        # Note: writing to the CSV on the server does not sync to GitHub.
        # For long-term storage, set up a database or a secure remote store.
