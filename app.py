# -*- coding: utf-8 -*-
import os
import pathlib
import anthropic
import streamlit as st

SECRETS_FILE = pathlib.Path(".streamlit/secrets.toml")

def load_saved_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    try:
        return st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        return ""

def persist_key(key: str) -> None:
    try:
        SECRETS_FILE.parent.mkdir(exist_ok=True)
        SECRETS_FILE.write_text(f'ANTHROPIC_API_KEY = "{key}"\n', encoding="utf-8")
    except OSError:
        pass  # read-only filesystem on Streamlit Cloud — key is already in st.secrets

st.set_page_config(page_title="Resume Tailor AI", page_icon="✦", layout="centered")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }

.stApp { background: #0f172a !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1e293b !important;
    border-right: 1px solid #1e3a5f !important;
}
section[data-testid="stSidebar"] * { color: #f1f5f9 !important; }
section[data-testid="stSidebar"] input {
    background: #0f172a !important;
    border: 1px solid #334155 !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
}

/* Block container */
.block-container { background: #0f172a !important; }

/* Text areas — aggressive overrides */
.stTextArea,
.stTextArea > div,
.stTextArea > div > div,
.stTextArea textarea,
div[data-testid="stTextArea"] textarea,
[data-baseweb="textarea"] textarea,
[data-baseweb="base-input"] textarea {
    background: #0f172a !important;
    background-color: #0f172a !important;
    color: #e2e8f0 !important;
    border-color: #334155 !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    line-height: 1.75 !important;
}
.stTextArea textarea:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: #475569 !important; }

/* Input text (API key) */
.stTextInput input,
div[data-testid="stTextInput"] input {
    background: #0f172a !important;
    color: #f1f5f9 !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}

/* Labels */
label, .stTextArea label, .stTextInput label,
[data-testid="stWidgetLabel"] {
    color: #94a3b8 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.6px !important;
    text-transform: uppercase !important;
}

/* Primary button */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 0.6rem 1.6rem !important;
    box-shadow: 0 4px 18px rgba(59,130,246,0.35) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(59,130,246,0.45) !important;
}

/* Back button (first column) */
[data-testid="column"]:first-child .stButton > button {
    background: transparent !important;
    border: 1px solid #334155 !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
}
[data-testid="column"]:first-child .stButton > button:hover {
    background: #1e293b !important;
    color: #f1f5f9 !important;
    transform: translateY(-1px) !important;
}

/* Download button */
.stDownloadButton > button {
    background: linear-gradient(135deg, #22c55e, #15803d) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    box-shadow: 0 4px 18px rgba(34,197,94,0.3) !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(34,197,94,0.4) !important;
}

/* File uploader */
[data-testid="stFileUploader"] section {
    background: #1e293b !important;
    border: 2px dashed #334155 !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"] section:hover { border-color: #3b82f6 !important; }
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span { color: #64748b !important; }

/* Alerts */
.stAlert {
    background: #1e293b !important;
    border-radius: 10px !important;
    border: 1px solid #334155 !important;
}

/* Markdown output */
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #93c5fd !important; }
.stMarkdown p, .stMarkdown li { color: #e2e8f0 !important; line-height: 1.8 !important; }
.stMarkdown strong { color: #f1f5f9 !important; }
.stMarkdown hr { border-color: #334155 !important; }

/* Spinner */
.stSpinner > div { border-top-color: #3b82f6 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0 0.5rem;">
        <div style="font-size:1.4rem;font-weight:800;
             background:linear-gradient(135deg,#93c5fd,#3b82f6);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            ✦ Resume Tailor AI
        </div>
        <div style="color:#475569;font-size:12px;margin-top:4px;">Powered by Claude</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    saved_key = load_saved_key()
    api_key = st.text_input(
        "Anthropic API Key",
        value=saved_key,
        type="password",
        placeholder="sk-ant-...",
        help="Get yours at console.anthropic.com",
    )

    if api_key and api_key != saved_key:
        if st.button("💾 Save key", use_container_width=True):
            persist_key(api_key)
            st.success("Key saved — won't ask again!")
            st.rerun()
    elif not api_key:
        st.warning("Add your API key to get started.")

    st.divider()
    st.markdown("""
    <div style="color:#64748b;font-size:13px;line-height:2.2;">
        <span style="color:#3b82f6;font-weight:700;">①</span>&nbsp; Paste or upload your resume<br>
        <span style="color:#3b82f6;font-weight:700;">②</span>&nbsp; Add the job description<br>
        <span style="color:#3b82f6;font-weight:700;">③</span>&nbsp; Get your tailored resume<br>
        <span style="color:#22c55e;font-weight:700;">⬇</span>&nbsp; Download as Markdown
    </div>
    """, unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────
for k, v in {"step": 1, "needs_generation": False,
             "saved_resume": "", "saved_jd": ""}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2.5rem 0 1rem;">
    <div style="font-size:2.6rem;font-weight:800;
         background:linear-gradient(135deg,#bfdbfe,#3b82f6,#1d4ed8);
         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
         letter-spacing:-1px;">
        Resume Tailor AI
    </div>
    <div style="color:#475569;font-size:0.9rem;margin-top:6px;letter-spacing:0.3px;">
        Tailored to your dream job — in seconds
    </div>
</div>
""", unsafe_allow_html=True)

# ── Step indicator ────────────────────────────────────────────────────────────
step = st.session_state["step"]

def render_step(n, label, current):
    if n < current:
        bg, fg, glow, lc, icon = "#22c55e", "#fff", "", "#22c55e", "&#10003;"
    elif n == current:
        bg, fg = "#3b82f6", "#fff"
        glow, lc, icon = "box-shadow:0 0 20px rgba(59,130,246,0.55);", "#3b82f6", str(n)
    else:
        bg, fg, glow, lc, icon = "#1e293b", "#475569", "", "#475569", str(n)
    # Single line — no indentation so markdown doesn't treat it as a code block
    return (f'<div style="display:flex;flex-direction:column;align-items:center;gap:7px;">'
            f'<div style="width:42px;height:42px;border-radius:50%;background:{bg};display:flex;'
            f'align-items:center;justify-content:center;color:{fg};font-weight:700;font-size:15px;{glow}">{icon}</div>'
            f'<div style="font-size:11px;font-weight:600;color:{lc};white-space:nowrap;">{label}</div>'
            f'</div>')

def render_line(done):
    color = "#3b82f6" if done else "#1e293b"
    return f'<div style="width:90px;height:2px;background:{color};margin-top:-21px;"></div>'

indicator = (
    '<div style="display:flex;align-items:flex-start;justify-content:center;gap:0;margin:0.5rem 0 2.5rem;">'
    + render_step(1, "Your Resume", step)
    + render_line(step > 1)
    + render_step(2, "Job Description", step)
    + render_line(step > 2)
    + render_step(3, "Tailored Result", step)
    + '</div>'
)
st.markdown(indicator, unsafe_allow_html=True)

# ── STEP 1 : Resume ───────────────────────────────────────────────────────────
if step == 1:
    st.markdown("""
    <div style="background:#1e293b;border:1px solid #1e3a5f;border-radius:14px;
                padding:1.5rem 2rem;margin-bottom:1.2rem;">
        <div style="font-size:1.2rem;font-weight:700;color:#f1f5f9;">📋 Your Resume</div>
        <div style="color:#64748b;font-size:0.82rem;margin-top:4px;">
            Upload a <code style="color:#3b82f6;">.txt</code> file <b>or</b> paste your resume below
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload resume (.txt)", type=["txt"])
    if uploaded is not None:
        # write into the text-area widget key so it shows in the box
        st.session_state["resume_area"] = uploaded.read().decode("utf-8")

    # initialise text area from whatever was saved before (Back navigation)
    if "resume_area" not in st.session_state:
        st.session_state["resume_area"] = st.session_state["saved_resume"]

    st.text_area("Or paste here", height=320, key="resume_area",
                 placeholder="Paste your full resume here…")

    _, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button("Next →", use_container_width=True):
            text = st.session_state.get("resume_area", "").strip()
            if text:
                # ← save to a NON-widget key so it survives step navigation
                st.session_state["saved_resume"] = text
                st.session_state["step"] = 2
                st.rerun()
            else:
                st.warning("Please add your resume before continuing.")

# ── STEP 2 : Job Description ──────────────────────────────────────────────────
elif step == 2:
    st.markdown("""
    <div style="background:#1e293b;border:1px solid #1e3a5f;border-radius:14px;
                padding:1.5rem 2rem;margin-bottom:1.2rem;">
        <div style="font-size:1.2rem;font-weight:700;color:#f1f5f9;">💼 Job Description</div>
        <div style="color:#64748b;font-size:0.82rem;margin-top:4px;">
            Paste the full job description you're applying for
        </div>
    </div>
    """, unsafe_allow_html=True)

    # restore JD if user hit Back from step 3
    if "jd_area" not in st.session_state:
        st.session_state["jd_area"] = st.session_state["saved_jd"]

    st.text_area("Paste job description here", height=320, key="jd_area",
                 placeholder="Paste the job description here…")

    col_back, _, col_btn = st.columns([1, 2, 1])
    with col_back:
        if st.button("← Back", use_container_width=True):
            st.session_state["step"] = 1
            st.rerun()
    with col_btn:
        if st.button("✨ Generate", use_container_width=True):
            jd_text = st.session_state.get("jd_area", "").strip()
            resume_text = st.session_state.get("saved_resume", "").strip()
            if not api_key:
                st.error("Enter your API key in the sidebar first.")
            elif not resume_text:
                st.warning("Resume is missing — go back and add it.")
            elif not jd_text:
                st.warning("Please paste a job description.")
            else:
                # save JD to non-widget key before navigating
                st.session_state["saved_jd"] = jd_text
                st.session_state.pop("last_output", None)
                st.session_state["needs_generation"] = True
                st.session_state["step"] = 3
                st.rerun()

# ── STEP 3 : Result ───────────────────────────────────────────────────────────
elif step == 3:
    st.markdown("""
    <div style="background:#1e293b;border:1px solid #1e3a5f;border-radius:14px;
                padding:1.5rem 2rem;margin-bottom:1.2rem;">
        <div style="font-size:1.2rem;font-weight:700;color:#f1f5f9;">✦ Tailored Resume</div>
        <div style="color:#64748b;font-size:0.82rem;margin-top:4px;">
            Optimised keywords &amp; structure for your target role
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("needs_generation"):
        resume = st.session_state["saved_resume"]
        jd     = st.session_state["saved_jd"]
        out_ph = st.empty()
        full_output = ""

        prompt = (
            "Rewrite this resume to align with the job description. "
            "Keep all facts truthful. Reorder and reword to match keywords. "
            "Format the output in clean, well-structured Markdown "
            "(use ## for sections, bold for job titles).\n\n"
            f"RESUME:\n{resume}\n\nJD:\n{jd}"
        )

        try:
            client = anthropic.Anthropic(api_key=api_key)
            with st.spinner("Crafting your tailored resume…"):
                with client.messages.stream(
                    model="claude-opus-4-5",
                    max_tokens=2048,
                    messages=[{"role": "user", "content": prompt}],
                ) as stream:
                    for text in stream.text_stream:
                        full_output += text
                        out_ph.markdown(full_output + " ▌")

            out_ph.markdown(full_output)
            st.session_state["last_output"] = full_output
            st.session_state["needs_generation"] = False

        except Exception as e:
            st.error(f"Generation failed: {e}")
            st.session_state["needs_generation"] = False

    elif "last_output" in st.session_state:
        output = st.session_state["last_output"]
        word_count = len(output.split())

        st.markdown(
            f'<div style="color:#475569;font-size:12px;margin-bottom:0.8rem;">~{word_count} words</div>',
            unsafe_allow_html=True,
        )
        st.markdown(output)

        st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

        col_back, _, col_dl = st.columns([1, 2, 1])
        with col_back:
            if st.button("← Start Over", use_container_width=True):
                for k in ["last_output", "needs_generation",
                          "saved_resume", "saved_jd",
                          "resume_area", "jd_area"]:
                    st.session_state.pop(k, None)
                st.session_state["step"] = 1
                st.rerun()
        with col_dl:
            st.download_button(
                "⬇️ Download",
                data=output,
                file_name="tailored_resume.md",
                mime="text/markdown",
                use_container_width=True,
            )
