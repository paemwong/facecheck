"""Custom CSS: navy theme, viewfinder-style hero, responsive layout."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #0A1628;
  --panel: #0F2140;
  --panel-2: #132A52;
  --line: #1E3A66;
  --accent: #3B82F6;
  --accent-2: #22D3EE;
  --text: #E6EDF7;
  --muted: #8FA3C0;
  --ok: #34D399;
  --bad: #F87171;
  --warn: #FBBF24;
}

html { scroll-behavior: smooth; }
.stApp {
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
  background:
    radial-gradient(900px 480px at 85% -10%, rgba(59,130,246,.16), transparent 60%),
    radial-gradient(700px 400px at -5% 20%, rgba(34,211,238,.07), transparent 60%),
    var(--bg);
}
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1100px; padding: 2rem 1.25rem 3rem; }

/* ---------- Hero with viewfinder corners ---------- */
.hero {
  position: relative;
  padding: 3.2rem 2.4rem 2.6rem;
  margin: .5rem 0 1.4rem;
  border-radius: 18px;
  background: linear-gradient(160deg, var(--panel) 0%, #0C1B36 100%);
  border: 1px solid var(--line);
}
.hero::before, .hero::after {
  content: ""; position: absolute; width: 38px; height: 38px;
  border: 3px solid var(--accent-2); opacity: .9; pointer-events: none;
}
.hero::before { top: 14px; left: 14px; border-right: 0; border-bottom: 0; border-top-left-radius: 10px; }
.hero::after  { bottom: 14px; right: 14px; border-left: 0; border-top: 0; border-bottom-right-radius: 10px; }
.hero h1 {
  font-size: 2.9rem; line-height: 1.08; font-weight: 800; letter-spacing: -0.02em;
  margin: 0 0 .55rem; color: var(--text); padding: 0;
}
.hero .subtitle { font-size: 1.2rem; font-weight: 500; color: var(--accent-2); margin: 0 0 1rem; }
.hero .desc { max-width: 62ch; color: #C3D0E6; font-size: 1.02rem; line-height: 1.65; margin: 0 0 1.5rem; }
.cta {
  display: inline-block; padding: .8rem 1.6rem; border-radius: 10px;
  background: var(--accent); color: #fff !important; font-weight: 600; text-decoration: none !important;
  box-shadow: 0 6px 20px rgba(59,130,246,.35); transition: background .15s, transform .15s;
}
.cta:hover { background: #2563EB; transform: translateY(-1px); }
.cta:focus-visible { outline: 3px solid var(--accent-2); outline-offset: 3px; }
.disclaimer {
  margin-top: 1.5rem; padding: .8rem 1rem; max-width: 70ch;
  border-left: 3px solid var(--warn); background: rgba(251,191,36,.07);
  color: #E8D9A8; font-size: .9rem; line-height: 1.55; border-radius: 0 8px 8px 0;
}

/* ---------- How it works ---------- */
.steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 2.2rem; }
.step { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 1rem 1.1rem; }
.step b { display: block; color: var(--text); margin-bottom: .25rem; }
.step span { color: var(--muted); font-size: .92rem; line-height: 1.5; }
.step i {
  font-style: normal; display: inline-flex; width: 1.6rem; height: 1.6rem; border-radius: 50%;
  align-items: center; justify-content: center; margin-right: .5rem;
  background: rgba(59,130,246,.2); color: var(--accent-2); font-size: .85rem; font-weight: 700;
}

/* ---------- Section titles ---------- */
.section-title { font-size: 1.7rem; font-weight: 700; margin: 1rem 0 .3rem; color: var(--text); }
.section-sub { color: var(--muted); margin-bottom: 1rem; }
.panel-title { font-size: 1.15rem; font-weight: 600; margin: .2rem 0 .7rem; color: var(--text); }

/* ---------- Streamlit widgets ---------- */
[data-testid="stFileUploaderDropzone"] {
  background: var(--panel); border: 2px dashed #2A4B80; border-radius: 14px; padding: 1.6rem 1rem;
  transition: border-color .15s, background .15s;
}
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--accent-2); background: var(--panel-2); }
[data-testid="stExpander"] { background: var(--panel); border: 1px solid var(--line); border-radius: 14px; }
[data-testid="stImage"] img { border-radius: 12px; border: 1px solid var(--line); max-width: 100%; }
.stButton > button, .stDownloadButton > button {
  width: 100%; border-radius: 10px; font-weight: 600; padding: .65rem 1rem;
  border: 1px solid var(--line); background: var(--panel); color: var(--text);
}
.stButton > button:hover { border-color: var(--accent); color: #fff; }
.stButton > button[kind="primary"], button[data-testid="stBaseButton-primary"] {
  background: var(--accent); border-color: var(--accent); color: #fff;
  box-shadow: 0 4px 16px rgba(59,130,246,.3);
}
.stButton > button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover { background: #2563EB; }
.stButton > button:disabled { opacity: .45; box-shadow: none; }

/* ---------- Status pills ---------- */
.pill { display: inline-block; padding: .3rem .8rem; border-radius: 999px; font-size: .88rem; font-weight: 600; margin: .4rem 0; }
.pill.ok   { background: rgba(52,211,153,.14); color: var(--ok);   border: 1px solid rgba(52,211,153,.4); }
.pill.warn { background: rgba(251,191,36,.12); color: var(--warn); border: 1px solid rgba(251,191,36,.4); }

/* ---------- Result card ---------- */
.placeholder {
  border: 1px dashed var(--line); border-radius: 14px; padding: 2.6rem 1.4rem; text-align: center;
  color: var(--muted); background: rgba(15,33,64,.5); line-height: 1.6;
}
.result { border-radius: 16px; padding: 1.5rem; background: var(--panel); border: 1px solid var(--line); border-top-width: 5px; }
.result.real { border-top-color: var(--ok); }
.result.fake { border-top-color: var(--bad); }
.result .label { color: var(--muted); font-size: .9rem; }
.result .verdict { font-size: 2.1rem; font-weight: 800; letter-spacing: -0.01em; margin: .15rem 0; }
.result.real .verdict { color: var(--ok); }
.result.fake .verdict { color: var(--bad); }
.result .conf { color: var(--text); font-size: 1.05rem; margin-bottom: 1.1rem; }
.bar-row { margin: .65rem 0; }
.bar-head { display: flex; justify-content: space-between; font-size: .92rem; color: #C3D0E6; margin-bottom: .3rem; }
.bar { height: 10px; border-radius: 999px; background: #0A1628; overflow: hidden; border: 1px solid var(--line); }
.bar > div { height: 100%; border-radius: 999px; }
.bar .g { background: linear-gradient(90deg, #10B981, var(--ok)); }
.bar .r { background: linear-gradient(90deg, #EF4444, var(--bad)); }
.note { margin-top: 1rem; padding: .7rem .9rem; border-radius: 8px; background: rgba(251,191,36,.08); color: #E8D9A8; font-size: .9rem; }
.meta { margin-top: 1rem; color: var(--muted); font-size: .85rem; line-height: 1.6; }

.footer { margin-top: 3rem; padding-top: 1.2rem; border-top: 1px solid var(--line); color: var(--muted); font-size: .88rem; text-align: center; line-height: 1.7; }

/* ---------- Mobile ---------- */
@media (max-width: 720px) {
  .block-container { padding: 1rem .8rem 2rem; }
  .hero { padding: 2.4rem 1.2rem 1.8rem; }
  .hero h1 { font-size: 2.05rem; }
  .hero .subtitle { font-size: 1.05rem; }
  .steps { grid-template-columns: 1fr; }
  .result .verdict { font-size: 1.7rem; }
  .section-title { font-size: 1.4rem; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  .cta, [data-testid="stFileUploaderDropzone"] { transition: none; }
}
</style>
"""
