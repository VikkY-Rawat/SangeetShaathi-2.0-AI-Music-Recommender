import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import streamlit as st
import pandas as pd
from src.core import SangeetEngine, get_feedback, save_feedback, init_db
from src.library import load_catalog, get_favorites, toggle_favorite, save_recent

st.set_page_config(page_title="SangeetShaathi 2.0", page_icon="🎵", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp{background:radial-gradient(ellipse at 12% 0%,#282044 0%,#151525 43%,#0b1018 100%);color:#f7f5ff}
.block-container{max-width:1440px;padding-top:3.5rem !important;padding-bottom:3rem !important}
[data-testid="stSidebar"]{background:#101522;border-right:1px solid #2e344a}
[data-testid="stSidebar"] *{color:#e8e8f4!important}
.hero{display:block;box-sizing:border-box;padding:2rem 2rem 1.8rem !important;min-height:180px;height:auto;margin-top:.5rem;margin-bottom:1.3rem;border:1px solid #4b426c;border-radius:24px;background:linear-gradient(120deg,rgba(112,78,184,.35),rgba(37,44,79,.48));box-shadow:0 12px 35px #0003;overflow:visible}
.hero h1{font-size:clamp(2rem,4vw,3rem);margin:0;color:#fbfaff;letter-spacing:-.04em}
.hero p{color:#d1c9ef;margin:.55rem 0 0;font-size:1rem}
.kicker{display:block;position:relative;color:#c4b5fd;text-transform:uppercase;letter-spacing:.14em;font-size:.75rem;font-weight:800;line-height:1.6;margin:0 0 .65rem;padding-top:.2rem;overflow:visible;white-space:normal}
.section-title{font-size:1.4rem;font-weight:780;margin:.7rem 0 .25rem;color:#faf9ff}
.helper{color:#b8bad0;font-size:.92rem;line-height:1.55}
.stTextArea textarea,.stTextInput input{background:#171b2a!important;color:#fff!important;-webkit-text-fill-color:#fff!important;border:1px solid #555b78!important;border-radius:12px!important;caret-color:#d9c5ff!important}
.stTextArea textarea::placeholder,.stTextInput input::placeholder{color:#a8acc4!important;-webkit-text-fill-color:#a8acc4!important;opacity:1!important}
[data-baseweb="select"]>div{background:#171b2a!important;color:#fff!important;border-color:#555b78!important;border-radius:10px!important}
[data-baseweb="select"] *{color:#fff!important}
.stSlider label,.stSelectbox label,.stTextArea label,.stTextInput label{color:#e9e7f5!important;font-weight:650!important}
.stButton>button,.stFormSubmitButton>button,.stLinkButton>a{background:linear-gradient(100deg,#8055e9,#6358d9)!important;color:#fff!important;border:1px solid #a78bfa!important;border-radius:12px!important;font-weight:700!important;min-height:2.55rem}
.stButton>button:hover,.stFormSubmitButton>button:hover,.stLinkButton>a:hover{background:linear-gradient(100deg,#9b75ff,#8274ff)!important;color:white!important;border-color:#c4b5fd!important}
div[data-testid="stMetric"]{background:rgba(27,30,49,.82);border:1px solid #353b55;padding:1rem;border-radius:16px}
div[data-testid="stMetricLabel"]{color:#bfc3dc!important} div[data-testid="stMetricValue"]{color:#f9f7ff!important}
div[data-testid="stExpander"]{border:1px solid #343a52;border-radius:14px;overflow:hidden}
.songcard{background:linear-gradient(145deg,rgba(31,35,56,.98),rgba(21,25,41,.98));border:1px solid #3b4260;border-radius:18px;padding:1.1rem 1.2rem;margin:.55rem 0;box-shadow:0 8px 20px #0002}
.songtitle{font-size:1.08rem;font-weight:780;color:#faf9ff;margin-bottom:.25rem}
.songmeta{font-size:.88rem;color:#b8bdd6;margin-bottom:.55rem}
.tag{display:inline-block;background:#30274d;border:1px solid #554477;color:#e4d7ff;padding:.2rem .55rem;border-radius:999px;font-size:.75rem;margin:.12rem .15rem .12rem 0}
div[data-testid="stProgress"]>div>div{background:#a78bfa}
hr{border-color:#30364d} footer{visibility:hidden}
</style>
<div class="hero">
  <div class="kicker">AI-powered music discovery</div>
  <h1>🎵 SangeetShaathi <span style="color:#c4b5fd">2.0</span></h1>
  <p>Your feelings, understood. Your music, personalized.</p>
</div>
""", unsafe_allow_html=True)

MOODS = [
    ("😊","Happy","happy joy uplifting"),("😢","Sad","sad sadness heartbreak"),
    ("💔","Emotional","heartbreak sadness emotional"),("😡","Angry","anger frustration intense"),
    ("😌","Calm","calm peaceful relax"),("⚡","Energetic","energy energetic party"),
    ("💪","Motivational","motivation hope uplifting"),("❤️","Romantic","love romance"),
    ("🌙","Sleep / Relax","calm peaceful sleep"),("🥳","Party","party joy energy"),
    ("🧠","Focus / Study","focus calm instrumental"),("🕰️","Nostalgic","nostalgia reflection"),
    ("🌧️","Lonely","lonely sadness reflection"),("🙏","Spiritual","spiritual peace hope"),
    ("🌈","Hopeful","hope uplifting joy")
]
MOOD_TO_TAGS = {
    "Happy":"joy|happy|uplifting|party","Sad":"sadness|sad|heartbreak|reflection",
    "Emotional":"sadness|heartbreak|love|reflection","Angry":"anger|frustration|energy",
    "Calm":"calm|peace|reflection|spiritual","Energetic":"energy|energetic|party|motivation",
    "Motivational":"motivation|hope|uplifting|energy","Romantic":"love|romance|joy",
    "Sleep / Relax":"calm|peace|relax|reflection","Party":"party|joy|energy",
    "Focus / Study":"calm|focus|reflection|instrumental","Nostalgic":"nostalgia|reflection|sadness",
    "Lonely":"lonely|sadness|reflection|heartbreak","Spiritual":"spiritual|calm|hope",
    "Hopeful":"hope|uplifting|joy|motivation"
}
init_db()
catalog=load_catalog()
if "page" not in st.session_state: st.session_state.page="Discover"
if "selected_mood" not in st.session_state: st.session_state.selected_mood=None
if "results" not in st.session_state: st.session_state.results=None

with st.sidebar:
    st.markdown("## 🎧 SangeetShaathi")
    st.caption("Your personal AI music companion")
    page=st.radio("Navigate",["Discover","AI Music Search","Explore Library","My Music","About & Insights"],index=["Discover","AI Music Search","Explore Library","My Music","About & Insights"].index(st.session_state.page),label_visibility="collapsed")
    st.session_state.page=page
    st.divider()
    st.metric("Songs in library",f"{len(catalog):,}")
    st.caption("Models run locally after the one-time download. External song links may require internet.")
    st.markdown("[Emotion model card](https://huggingface.co/tabularisai/multilingual-emotion-classification)")
    st.markdown("[Embedding model card](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)")

@st.cache_resource(show_spinner="Loading local AI models...")
def load_engine():
    return SangeetEngine()

def run_recommendation(prompt, top_k=8):
    try:
        engine=load_engine()
        fb=get_feedback()
        liked=fb.loc[fb.action=="like","song_id"].tolist() if not fb.empty else []
        disliked=fb.loc[fb.action=="dislike","song_id"].tolist() if not fb.empty else []
        with st.spinner("Understanding your request and ranking songs..."):
            result=engine.recommend(prompt,top_k=top_k,liked_ids=liked,disliked_ids=disliked)
        st.session_state.results=(result,prompt)
        save_recent(prompt)
    except Exception as exc:
        st.error("AI models could not be loaded. Run `python download_models.py` once while connected to the internet.")
        st.code(str(exc))

def render_results():
    if not st.session_state.results: return
    (emotion,scores,intent,mood,songs),prompt=st.session_state.results
    st.markdown('<div class="section-title">Your personalized playlist</div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    a.metric("Detected emotion",str(emotion).replace("_"," ").title())
    b.metric("Request intent",str(intent).title())
    c.metric("Recommendations",len(songs))
    with st.expander("View emotion model scores"):
        score_df=pd.DataFrame(sorted(scores.items(),key=lambda x:x[1],reverse=True),columns=["Emotion","Score"])
        score_df["Score"]=score_df["Score"].map(lambda v:f"{v:.1%}")
        st.dataframe(score_df,use_container_width=True,hide_index=True)
        st.caption("Scores are model estimates, not definitive statements about your feelings.")
    favs=set(get_favorites())
    for _,song in songs.iterrows():
        sid=int(song["song_id"])
        st.markdown('<div class="songcard">',unsafe_allow_html=True)
        left,mid,right=st.columns([3.5,1.3,1.6],gap="medium")
        with left:
            st.markdown(f'<div class="songtitle">🎧 {song["title"]}</div>',unsafe_allow_html=True)
            st.markdown(f'<div class="songmeta">{song["artist"]} · {song.get("year","")} · {song.get("language","Hindi")}</div>',unsafe_allow_html=True)
            if str(song.get("album","")) not in ("","nan","None"): st.caption(f"Album: {song.get('album')}")
            st.write(str(song.get("description","")) or "Discover this track.")
            tags="".join(f'<span class="tag">{t.strip().title()}</span>' for t in str(song.get("mood_tags","")).split("|") if t.strip())
            st.markdown(tags,unsafe_allow_html=True)
        with mid:
            sc=float(song.get("final_score",0))
            st.caption("Relative match score")
            st.progress(max(0.0,min(1.0,sc)))
            st.markdown(f"**{sc:.3f}**")
        with right:
            link=str(song.get("link",""))
            if link and link.startswith("http"): st.link_button("▶ Find song",link,use_container_width=True)
            else: st.caption("No external link available")
            x,y=st.columns(2)
            if x.button("👍",key=f"like_{sid}",help="Like this song"):
                save_feedback(sid,"like"); st.toast("Like saved for future recommendations.")
            if y.button("👎",key=f"dislike_{sid}",help="Dislike this song"):
                save_feedback(sid,"dislike"); st.toast("Dislike saved.")
            if st.button("★ Saved" if sid in favs else "☆ Save",key=f"fav_{sid}",use_container_width=True):
                toggle_favorite(sid); st.toast("Favorites updated."); st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

if page=="Discover":
    st.markdown('<div class="section-title">What’s your vibe today?</div>',unsafe_allow_html=True)
    st.markdown('<div class="helper">Pick a mood to get started, or describe your feelings in your own words.</div>',unsafe_allow_html=True)
    for start in range(0,len(MOODS),5):
        cols=st.columns(5,gap="small")
        for col,(emoji,label,terms) in zip(cols,MOODS[start:start+5]):
            with col:
                selected=st.session_state.selected_mood==label
                if st.button(f"{emoji}  {label}"+(" ✓" if selected else ""),key=f"mood_{label}",use_container_width=True):
                    st.session_state.selected_mood=label
                    st.session_state.results=None
                    st.rerun()
    selected=st.session_state.selected_mood
    if selected:
        st.info(f"Selected mood: {selected}. You can still tell us what kind of songs you want.")
    with st.form("discover_form"):
        query=st.text_area("Describe your mood (optional)",placeholder="Example: Aaj low feel kar raha hoon, kuch hopeful Hindi songs suggest karo...",height=95)
        count=st.slider("Songs to recommend",4,12,8)
        go=st.form_submit_button("✨ Create my playlist",use_container_width=True)
    if go:
        parts=[]
        if selected: parts.append(f"I want {selected} Hindi songs. Mood tags: {MOOD_TO_TAGS.get(selected,'')}.")
        if query.strip(): parts.append(query.strip())
        if not parts: st.warning("Select a mood or describe what you want.")
        else: run_recommendation(" ".join(parts),count)
    render_results()

elif page=="AI Music Search":
    st.markdown('<div class="section-title">AI Music Search</div>',unsafe_allow_html=True)
    st.markdown('<div class="helper">Describe the mood, context, or kind of music you want in Hindi, English, or Hinglish.</div>',unsafe_allow_html=True)
    with st.form("ai_search"):
        query=st.text_area("Your request",placeholder="Aaj bahut akela feel kar raha hoon, aise gaane batao jo mujhe better feel karayein.",height=140)
        count=st.slider("Number of songs",4,12,8,key="ai_count")
        submitted=st.form_submit_button("Understand and recommend",use_container_width=True)
    if submitted:
        if len(query.strip())<3: st.warning("Please enter a little more detail.")
        else: run_recommendation(query.strip(),count)
    render_results()

elif page=="Explore Library":
    st.markdown('<div class="section-title">Explore the music library</div>',unsafe_allow_html=True)
    st.caption(f"{len(catalog):,} unique catalog records loaded from the current CSV after basic validation.")
    search=st.text_input("Search title, artist, album or description",placeholder="Search Arijit Singh, romance, Ilahi...")
    all_moods=sorted({t.strip() for v in catalog["mood_tags"].fillna("").astype(str) for t in v.split("|") if t.strip()})
    f1,f2,f3=st.columns(3)
    with f1: mood_filter=st.selectbox("Mood tag",["All moods"]+all_moods)
    with f2: language_filter=st.selectbox("Language",["All languages"]+sorted(catalog["language"].fillna("Unknown").astype(str).unique().tolist()))
    with f3: sort_by=st.selectbox("Sort by",["Title A–Z","Newest year","Oldest year"])
    df=catalog.copy()
    if search.strip():
        mask=pd.Series(False,index=df.index)
        for col in ["title","artist","album","description","genre"]:
            if col in df: mask |= df[col].fillna("").astype(str).str.contains(search.strip(),case=False,regex=False)
        df=df[mask]
    if mood_filter!="All moods": df=df[df["mood_tags"].fillna("").astype(str).str.contains(mood_filter,case=False,regex=False)]
    if language_filter!="All languages": df=df[df["language"].astype(str)==language_filter]
    if sort_by=="Title A–Z": df=df.sort_values("title")
    elif sort_by=="Newest year": df=df.sort_values("year",ascending=False,na_position="last")
    else: df=df.sort_values("year",ascending=True,na_position="last")
    st.write(f"**{len(df):,} songs match your filters**")
    page_size=20
    total_pages=max(1,(len(df)+page_size-1)//page_size)
    page_num=st.number_input("Page",min_value=1,max_value=total_pages,value=1,step=1)
    st.dataframe(df.iloc[(page_num-1)*page_size:page_num*page_size][["title","artist","album","year","language","genre","mood_tags","link"]],use_container_width=True,hide_index=True)
    st.caption("Use the external song link to find the track. The app does not host copyrighted audio.")

elif page=="My Music":
    st.markdown('<div class="section-title">My Music</div>',unsafe_allow_html=True)
    favorites=get_favorites()
    fb=get_feedback()
    if not favorites: st.info("No favorites saved yet. Open Discover and use ☆ Save on a song.")
    else:
        fav_df=catalog[catalog.song_id.isin(favorites)]
        st.write(f"**{len(fav_df)} saved songs**")
        for _,row in fav_df.iterrows():
            c1,c2,c3=st.columns([4,2,1])
            c1.markdown(f"**{row['title']}**  \n{row['artist']}")
            if row.get("link",""): c2.link_button("Find song",row["link"],use_container_width=True)
            if c3.button("Remove",key=f"remove_{row['song_id']}"):
                toggle_favorite(int(row["song_id"])); st.rerun()
    st.divider()
    st.markdown("### Feedback history")
    if fb.empty: st.caption("Likes and dislikes will appear here after you interact with recommendations.")
    else:
        st.dataframe(fb.sort_values("id",ascending=False).head(30),use_container_width=True,hide_index=True)

else:
    st.markdown('<div class="section-title">About & Model Insights</div>',unsafe_allow_html=True)
    st.markdown("""
    **Deep Learning:** multilingual Transformer emotion classification.  
    **NLP:** multilingual sentence embeddings and cosine similarity.  
    **Recommendation:** semantic relevance, mood tags and explicit feedback.  
    **Storage:** SQLite favorites and likes/dislikes.  
    **Offline behavior:** model inference uses local model files after setup; external song links may need internet.
    """)
    st.warning("Emotion estimates may be inaccurate for sarcasm, slang, and code-mixed text. Recommendation scores are ranking signals, not calibrated probabilities.")
    st.markdown("### Dataset integrity")
    st.write(f"Current catalog contains **{len(catalog):,}** usable unique records. Run the dataset import pipeline to expand it with a properly licensed source.")
    st.markdown("### Evaluation")
    st.write("Use the included test command and evaluation instructions. No model accuracy or recommendation quality score is claimed until measured on a labelled test set.")
    st.markdown("[MIT-licensed Bollywood metadata dataset](https://github.com/MrAsacker/bollywood-songs-metadata)")
