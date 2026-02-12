import streamlit as st
import streamlit.components.v1 as components
import random
import re
import time
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 (System Configuration) ---
st.set_page_config(
    page_title="O Mimaliay - 熱血球場", 
    page_icon="🏀", 
    layout="centered"
)

# --- 1. 資料庫 (第 7 課：O Mimaliay) ---
VOCAB_MAP = {
    "mimali": "打球", "kami": "我們(排除)", "i": "在", "kacomikayan": "運動場",
    "o": "焦點標記", "lan-ciw": "籃球", "ko": "主格標記", "kimalian": "玩的項目",
    "niyam": "我們的(排除)", "mafana'": "會/知道", "kiso": "你", "a": "連接詞",
    "hai": "是的", "maolah": "喜歡", "kako": "我", "malipahak": "快樂",
    "misalama": "玩耍", "pang-ciw": "棒球", "kita": "咱們(包含)"
}

VOCABULARY = [
    {"amis": "mimali", "zh": "打球", "emoji": "⛹️", "root": "mali", "root_zh": "球"},
    {"amis": "lan-ciw", "zh": "籃球", "emoji": "🏀", "root": "lan-ciw", "root_zh": "籃球(外來語)"},
    {"amis": "kimalian", "zh": "玩的項目", "emoji": "📋", "root": "mali", "root_zh": "球"},
    {"amis": "mafana'", "zh": "會/知道", "emoji": "💡", "root": "fana'", "root_zh": "知識"},
    {"amis": "maolah", "zh": "喜歡/愛", "emoji": "❤️", "root": "olah", "root_zh": "愛"},
    {"amis": "malipahak", "zh": "快樂", "emoji": "😄", "root": "lipahak", "root_zh": "快樂"},
    {"amis": "misalama", "zh": "玩耍", "emoji": "🤹", "root": "salama", "root_zh": "玩"},
    {"amis": "kacomikayan", "zh": "運動場", "emoji": "🏟️", "root": "cikay", "root_zh": "跑"},
    {"amis": "mi-", "zh": "做...(動作前綴)", "emoji": "🏃", "root": "mi", "root_zh": "主動"},
    {"amis": "ma-", "zh": "感到...(狀態前綴)", "emoji": "😌", "root": "ma", "root_zh": "狀態/能力"},
]

SENTENCES = [
    {
        "amis": "Mimali kami i kacomikayan.", 
        "zh": "我們在運動場打球。", 
        "note": """
        <br><b>Mimali</b>：打球 (<i>mi-</i> 動作)。
        <br><b>kami</b>：我們 (排除式，不含聽者)。
        <br><b>kacomikayan</b>：運動場 (跑的地方)。"""
    },
    {
        "amis": "O lan-ciw ko kimalian niyam.", 
        "zh": "我們打的是籃球。", 
        "note": """
        <br><b>O lan-ciw</b>：是籃球 (焦點)。
        <br><b>kimalian</b>：被玩的項目。
        <br><b>句型</b>：分裂句，強調「打的項目是什麼」。"""
    },
    {
        "amis": "Mafana' kiso a mimali?", 
        "zh": "你會打球嗎？", 
        "note": """
        <br><b>Mafana'</b>：會/懂得 (能力動詞)。
        <br><b>a</b>：連接詞。
        <br><b>結構</b>：Mafana' (能力) + 主詞 + a + 動作。"""
    },
    {
        "amis": "Hai, maolah kako a mimali.", 
        "zh": "是的，我很喜歡打球。", 
        "note": """
        <br><b>maolah</b>：喜歡 (<i>ma-</i> 情緒/狀態)。
        <br><b>mimali</b>：打球 (<i>mi-</i> 動作)。
        <br><b>對比</b>：<i>ma-</i> (非自願/感覺) vs <i>mi-</i> (意志/動作)。"""
    },
    {
        "amis": "Malipahak kami a misalama.", 
        "zh": "我們玩得很開心。", 
        "note": """
        <br><b>Malipahak</b>：快樂的 (形容詞性動詞)。
        <br><b>misalama</b>：玩耍。
        <br><b>語意</b>：我們處於快樂的狀態去玩。"""
    }
]

STORY_DATA = [
    {"amis": "Mimali kami i kacomikayan.", "zh": "我們在運動場打球。"},
    {"amis": "O lan-ciw ko kimalian niyam.", "zh": "我們打的是籃球。"},
    {"amis": "Mafana' kiso a mimali?", "zh": "你會打球嗎？"},
    {"amis": "Hai, maolah kako a mimali.", "zh": "是的，我很喜歡打球。"},
    {"amis": "Malipahak kami a misalama.", "zh": "我們玩得很開心。"}
]

# --- 2. 視覺系統 (CSS 注入 - Court Energy Theme) ---
st.markdown("""
    <style>
    /* 引入 Russo One (運動風) 和 Noto Sans TC */
    @import url('https://fonts.googleapis.com/css2?family=Russo+One&family=Noto+Sans+TC:wght@300;500;700&display=swap');
    
    /* 背景：深藍黑，對比強烈 */
    .stApp { background-color: #263238; color: #ECEFF1; font-family: 'Noto Sans TC', sans-serif; }
    
    /* 頭部：計分板風格 */
    .header-container { 
        background: #212121; 
        border: 4px solid #FF6D00;
        border-radius: 8px; 
        padding: 30px; 
        text-align: center; 
        margin-bottom: 30px; 
        box-shadow: 0 0 20px rgba(255, 109, 0, 0.3);
        position: relative;
    }
    
    .main-title { 
        font-family: 'Russo One', sans-serif; 
        color: #FF6D00; 
        font-size: 48px; 
        text-transform: uppercase;
        margin-bottom: 5px; 
        letter-spacing: 2px;
        text-shadow: 2px 2px 0 #000;
    }
    
    .sub-title { 
        color: #FFF; 
        font-size: 18px; 
        font-family: 'Russo One', sans-serif;
        background: #FF6D00;
        padding: 5px 20px;
        display: inline-block;
        transform: skew(-10deg); /* 傾斜效果，增加動感 */
    }
    
    /* Tab 樣式：強烈對比 */
    .stTabs [data-baseweb="tab"] { 
        color: #90A4AE !important; 
        font-family: 'Russo One', sans-serif;
        font-size: 18px;
        text-transform: uppercase;
    }
    .stTabs [aria-selected="true"] { 
        border-bottom: 4px solid #FF6D00 !important; 
        color: #FF6D00 !important; 
    }
    
    /* 按鈕：球場風格 */
    .stButton>button { 
        border: 2px solid #FF6D00 !important; 
        background: transparent !important; 
        color: #FF6D00 !important; 
        font-family: 'Russo One', sans-serif !important;
        font-size: 18px !important;
        width: 100%; 
        border-radius: 0; 
        transition: 0.2s; 
        text-transform: uppercase;
    }
    .stButton>button:hover { 
        background: #FF6D00 !important; 
        color: #000 !important; 
        box-shadow: 0 0 15px rgba(255, 109, 0, 0.6);
    }
    
    /* 測驗卡片：戰術板風格 */
    .quiz-card { 
        background: #ECEFF1; 
        border-top: 6px solid #FF6D00; 
        padding: 25px; 
        border-radius: 4px; 
        margin-bottom: 20px; 
        color: #263238;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .quiz-tag { 
        background: #263238; 
        color: #FF6D00; 
        padding: 4px 12px; 
        font-weight: bold; 
        font-size: 14px; 
        margin-right: 10px; 
        font-family: 'Russo One', sans-serif;
        text-transform: uppercase;
    }
    
    /* 翻譯區塊：教練筆記風格 */
    .zh-translation-block {
        background: #37474F;
        border-left: 4px solid #FF6D00;
        padding: 20px;
        margin-top: 0px; 
        color: #B0BEC5;
        font-size: 16px;
        line-height: 2.0;
        font-family: 'Noto Sans TC', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 核心技術：沙盒渲染引擎 (v9.7 - Sport Edition) ---
def get_html_card(item, type="word"):
    pt = "100px" if type == "full_amis_block" else "80px"
    mt = "-40px" if type == "full_amis_block" else "-30px" 

    style_block = f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Russo+One&family=Noto+Sans+TC:wght@300;500;700&display=swap');
        body {{ background-color: transparent; color: #ECEFF1; font-family: 'Noto Sans TC', sans-serif; margin: 0; padding: 5px; padding-top: {pt}; overflow-x: hidden; }}
        
        /* 互動單字：橘色實線 */
        .interactive-word {{ position: relative; display: inline-block; border-bottom: 3px solid #FF6D00; cursor: pointer; margin: 0 3px; color: #FFF; transition: 0.3s; font-size: 19px; font-weight: bold; }}
        .interactive-word:hover {{ color: #FF6D00; background: rgba(255, 109, 0, 0.1); }}
        
        .interactive-word .tooltip-text {{ visibility: hidden; min-width: 80px; background-color: #FF6D00; color: #000; text-align: center; border: 2px solid #FFF; padding: 6px; position: absolute; z-index: 100; bottom: 145%; left: 50%; transform: translateX(-50%); opacity: 0; transition: opacity 0.2s; font-size: 14px; white-space: nowrap; box-shadow: 0 4px 10px rgba(0,0,0,0.5); font-family: 'Russo One', sans-serif; }}
        .interactive-word:hover .tooltip-text {{ visibility: visible; opacity: 1; }}
        
        .play-btn-inline {{ background: #FF6D00; border: none; color: #000; border-radius: 0; width: 28px; height: 28px; cursor: pointer; margin-left: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; transition: 0.2s; vertical-align: middle; transform: skew(-10deg); }}
        .play-btn-inline:hover {{ background: #FFF; transform: skew(-10deg) scale(1.1); }}
        
        /* 單字卡樣式 - 球員卡風格 */
        .word-card-static {{ background: #ECEFF1; border-left: 8px solid #FF6D00; padding: 15px; display: flex; justify-content: space-between; align-items: center; margin-top: {mt}; height: 100px; box-sizing: border-box; box-shadow: 0 4px 8px rgba(0,0,0,0.3); transform: skew(-5deg); margin-left: 10px; margin-right: 10px; }}
        .word-card-inner {{ transform: skew(5deg); width: 100%; display: flex; justify-content: space-between; align-items: center; }} /* 修正內容傾斜 */
        
        .wc-root-tag {{ font-size: 12px; background: #263238; color: #FF6D00; padding: 2px 6px; font-weight: bold; margin-right: 5px; font-family: 'Russo One', sans-serif; text-transform: uppercase; }}
        .wc-amis {{ color: #263238; font-size: 26px; font-weight: 800; margin: 2px 0; font-family: 'Russo One', sans-serif; }}
        .wc-zh {{ color: #546E7A; font-size: 16px; font-weight: 500; }}
        .play-btn-large {{ background: #263238; border: 2px solid #FF6D00; color: #FF6D00; border-radius: 50%; width: 42px; height: 42px; cursor: pointer; font-size: 20px; transition: 0.2s; }}
        .play-btn-large:hover {{ background: #FF6D00; color: #000; }}
        
        .amis-full-block {{ line-height: 2.2; font-size: 18px; margin-top: {mt}; }}
        .sentence-row {{ margin-bottom: 12px; display: block; }}
    </style>
    <script>
        function speak(text) {{ window.speechSynthesis.cancel(); var msg = new SpeechSynthesisUtterance(); msg.text = text; msg.lang = 'id-ID'; msg.rate = 0.9; window.speechSynthesis.speak(msg); }}
    </script>"""

    header = f"<!DOCTYPE html><html><head>{style_block}</head><body>"
    body = ""
    
    if type == "word":
        v = item
        body = f"""<div class="word-card-static">
            <div class="word-card-inner">
                <div>
                    <div style="margin-bottom:5px;"><span class="wc-root-tag">ROOT: {v['root']}</span> <span style="font-size:12px; color:#78909C;">({v['root_zh']})</span></div>
                    <div class="wc-amis">{v['emoji']} {v['amis']}</div>
                    <div class="wc-zh">{v['zh']}</div>
                </div>
                <button class="play-btn-large" onclick="speak('{v['amis'].replace("'", "\\'")}')">🔊</button>
            </div>
        </div>"""

    elif type == "full_amis_block": 
        all_sentences_html = []
        for sentence_data in item:
            s_amis = sentence_data['amis']
            words = s_amis.split()
            parts = []
            for w in words:
                clean_word = re.sub(r"[^\w']", "", w).lower()
                translation = VOCAB_MAP.get(clean_word, "")
                js_word = clean_word.replace("'", "\\'") 
                
                if translation:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
                else:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
                parts.append(chunk)
            
            full_amis_js = s_amis.replace("'", "\\'")
            sentence_html = f"""
            <div class="sentence-row">
                {' '.join(parts)}
                <button class="play-btn-inline" onclick="speak('{full_amis_js}')" title="播放此句">🔊</button>
            </div>
            """
            all_sentences_html.append(sentence_html)
            
        body = f"""<div class="amis-full-block">{''.join(all_sentences_html)}</div>"""
    
    elif type == "sentence": 
        s = item
        words = s['amis'].split()
        parts = []
        for w in words:
            clean_word = re.sub(r"[^\w']", "", w).lower()
            translation = VOCAB_MAP.get(clean_word, "")
            js_word = clean_word.replace("'", "\\'") 
            
            if translation:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
            else:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
            parts.append(chunk)
            
        full_js = s['amis'].replace("'", "\\'")
        body = f'<div style="font-size: 18px; line-height: 1.6; margin-top: {mt};">{" ".join(parts)}</div><button style="margin-top:10px; background:#FF6D00; border:none; color:#000; padding:6px 15px; transform:skew(-10deg); cursor:pointer; font-family:Russo One; font-size:14px;" onclick="speak(`{full_js}`)">▶ PLAY AUDIO</button>'

    return header + body + "</body></html>"

# --- 4. 測驗生成引擎 ---
def generate_quiz():
    questions = []
    
    # 1. 聽音辨義
    q1 = random.choice(VOCABULARY)
    q1_opts = [q1['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q1], 2)]
    random.shuffle(q1_opts)
    questions.append({"type": "listen", "tag": "🎧 聽音辨義", "text": "請聽語音，選擇正確的單字", "audio": q1['amis'], "correct": q1['amis'], "options": q1_opts})
    
    # 2. 中翻阿
    q2 = random.choice(VOCABULARY)
    q2_opts = [q2['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q2], 2)]
    random.shuffle(q2_opts)
    questions.append({"type": "trans", "tag": "🧩 中翻阿", "text": f"請選擇「<span style='color:#FF6D00'>{q2['zh']}</span>」的阿美語", "correct": q2['amis'], "options": q2_opts})
    
    # 3. 阿翻中
    q3 = random.choice(VOCABULARY)
    q3_opts = [q3['zh']] + [v['zh'] for v in random.sample([x for x in VOCABULARY if x != q3], 2)]
    random.shuffle(q3_opts)
    questions.append({"type": "trans_a2z", "tag": "🔄 阿翻中", "text": f"單字 <span style='color:#FF6D00'>{q3['amis']}</span> 的意思是？", "correct": q3['zh'], "options": q3_opts})

    # 4. 詞根偵探
    q4 = random.choice(VOCABULARY)
    other_roots = list(set([v['root'] for v in VOCABULARY if v['root'] != q4['root']]))
    if len(other_roots) < 2: other_roots += ["roma", "lalan", "cidal"]
    q4_opts = [q4['root']] + random.sample(other_roots, 2)
    random.shuffle(q4_opts)
    questions.append({"type": "root", "tag": "🧬 詞根偵探", "text": f"單字 <span style='color:#FF6D00'>{q4['amis']}</span> 的詞根是？", "correct": q4['root'], "options": q4_opts, "note": f"詞根意思：{q4['root_zh']}"})
    
    # 5. 語感聽解
    q5 = random.choice(STORY_DATA)
    questions.append({"type": "listen_sent", "tag": "🔊 語感聽解", "text": "請聽句子，選擇正確的中文翻譯", "audio": q5['amis'], "correct": q5['zh'], "options": [q5['zh']] + [s['zh'] for s in random.sample([x for x in STORY_DATA if x != q5], 2)]})

    # 6. 句型翻譯
    q6 = random.choice(STORY_DATA)
    q6_opts = [q6['amis']] + [s['amis'] for s in random.sample([x for x in STORY_DATA if x != q6], 2)]
    random.shuffle(q6_opts)
    questions.append({"type": "sent_trans", "tag": "📝 句型翻譯", "text": f"請選擇中文「<span style='color:#FF6D00'>{q6['zh']}</span>」對應的阿美語", "correct": q6['amis'], "options": q6_opts})

    # 7. 克漏字
    q7 = random.choice(STORY_DATA)
    words = q7['amis'].split()
    valid_indices = []
    for i, w in enumerate(words):
        clean_w = re.sub(r"[^\w']", "", w).lower()
        if clean_w in VOCAB_MAP:
            valid_indices.append(i)
    
    if valid_indices:
        target_idx = random.choice(valid_indices)
        target_raw = words[target_idx]
        target_clean = re.sub(r"[^\w']", "", target_raw).lower()
        
        words_display = words[:]
        words_display[target_idx] = "______"
        q_text = " ".join(words_display)
        
        correct_ans = target_clean
        distractors = [k for k in VOCAB_MAP.keys() if k != correct_ans and len(k) > 2]
        if len(distractors) < 2: distractors += ["kako", "ira"]
        opts = [correct_ans] + random.sample(distractors, 2)
        random.shuffle(opts)
        
        questions.append({"type": "cloze", "tag": "🕳️ 文法克漏字", "text": f"請填空：<br><span style='color:#263238; font-size:18px;'>{q_text}</span><br><span style='color:#546E7A; font-size:14px;'>{q7['zh']}</span>", "correct": correct_ans, "options": opts})
    else:
        questions.append(questions[0]) 

    questions.append(random.choice(questions[:4])) 
    random.shuffle(questions)
    return questions

def play_audio_backend(text):
    try:
        tts = gTTS(text=text, lang='id'); fp = BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    except: pass

# --- 5. UI 呈現層 ---
st.markdown("""
<div class="header-container">
    <h1 class="main-title">O Mimaliay</h1>
    <div class="sub-title">第 7 課：熱血球場</div>
    <div style="font-size: 12px; margin-top:10px; color:#B0BEC5; font-family: 'Russo One', sans-serif;">Code-CRF v6.4 | Theme: Court Energy</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🏀 互動課文", 
    "🏃 核心單字", 
    "🧬 句型解析", 
    "⚔️ 實戰測驗"
])

with tab1:
    st.markdown("### // 文章閱讀")
    st.caption("👆 點擊單字可聽發音並查看翻譯")
    
    st.markdown("""<div style="background:#263238; padding:10px; border: 2px solid #FF6D00; border-radius:4px;">""", unsafe_allow_html=True)
    components.html(get_html_card(STORY_DATA, type="full_amis_block"), height=400, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    zh_content = "<br>".join([item['zh'] for item in STORY_DATA])
    st.markdown(f"""
    <div class="zh-translation-block">
        {zh_content}
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("### // 單字與詞根")
    for v in VOCABULARY:
        components.html(get_html_card(v, type="word"), height=150)

with tab3:
    st.markdown("### // 語法結構分析")
    for s in SENTENCES:
        st.markdown("""<div style="background:#ECEFF1; padding:15px; border-left: 6px solid #FF6D00; border-radius: 4px; margin-bottom:15px; color:#263238;">""", unsafe_allow_html=True)
        components.html(get_html_card(s, type="sentence"), height=160)
        st.markdown(f"""
        <div style="color:#263238; font-size:16px; margin-bottom:10px; border-top:1px solid #CFD8DC; padding-top:10px;">{s['zh']}</div>
        <div style="color:#546E7A; font-size:14px; line-height:1.8; border-top:1px dashed #CFD8DC; padding-top:5px;"><span style="color:#FF6D00; font-family:Russo One; font-weight:bold;">ANALYSIS:</span> {s.get('note', '')}</div>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = generate_quiz()
        st.session_state.quiz_step = 0; st.session_state.quiz_score = 0
    
    if st.session_state.quiz_step < len(st.session_state.quiz_questions):
        q = st.session_state.quiz_questions[st.session_state.quiz_step]
        st.markdown(f"""<div class="quiz-card"><div style="margin-bottom:10px;"><span class="quiz-tag">{q['tag']}</span> <span style="color:#546E7A;">Q{st.session_state.quiz_step + 1}</span></div><div style="font-size:18px; color:#263238; margin-bottom:10px;">{q['text']}</div></div>""", unsafe_allow_html=True)
        if 'audio' in q: play_audio_backend(q['audio'])
        opts = q['options']; cols = st.columns(min(len(opts), 3))
        for i, opt in enumerate(opts):
            with cols[i % 3]:
                if st.button(opt, key=f"q_{st.session_state.quiz_step}_{i}"):
                    if opt.lower() == q['correct'].lower():
                        st.success("✅ 正確 (Correct)"); st.session_state.quiz_score += 1
                    else:
                        st.error(f"❌ 錯誤 - 正解: {q['correct']}"); 
                        if 'note' in q: st.info(q['note'])
                    time.sleep(1.5); st.session_state.quiz_step += 1; st.rerun()
    else:
        st.markdown(f"""<div style="text-align:center; padding:30px; border:4px solid #FF6D00; border-radius:8px; background:#263238;"><h2 style="color:#FF6D00; font-family:Russo One;">MISSION COMPLETE</h2><p style="font-size:20px; color:#FFF;">得分: {st.session_state.quiz_score} / {len(st.session_state.quiz_questions)}</p></div>""", unsafe_allow_html=True)
        if st.button("🔄 重新挑戰 (Reboot)"): del st.session_state.quiz_questions; st.rerun()

st.markdown("---")
st.caption("Powered by Code-CRF v6.4 | Architecture: Chief Architect")
