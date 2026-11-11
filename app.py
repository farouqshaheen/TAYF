"""طيف — مختبر تفاعلي لمحاكاة التحقيق في الروابط اللاسلكية."""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from analysis.diagnosis import rank_suspects
from analysis.metrics import compare_phases
from analysis.mentor import mentor_guidance
from reporting.report_generator import export_dataframe_csv, generate_case_summary_text
from simulation.data_generator import run_simulation
from simulation.scenarios import LinkParams
from visualization.interactive_ber import create_interactive_ber
from visualization.interactive_constellation import create_rich_constellation
from visualization.interactive_heatmap import create_rich_heatmap
from visualization.interactive_oscilloscope import create_interactive_heartbeat
from visualization.interactive_radar import create_interactive_radar
from visualization.doctor_3d_component import get_doctor_3d_html
import streamlit.components.v1 as components

st.set_page_config(
    page_title="طيف | مختبر الإشارات اللاسلكية",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap');
:root { --ink:#e7edf5; --muted:#91a2b8; --line:#243449; --panel:#0d1724; --cyan:#52e0d1; --amber:#ffbd69; }
html, body, [class*="css"], [data-testid="stAppViewContainer"] { font-family:'IBM Plex Sans Arabic',sans-serif; direction:rtl; }
.stApp { background:radial-gradient(ellipse at 18% 0%,#10263a 0%,#08111b 43%,#070c13 100%); color:var(--ink); }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0b1622,#09111a); border-left:1px solid var(--line); }
.block-container { max-width:1500px; padding-top:1.35rem; padding-bottom:3rem; }
h1,h2,h3 { letter-spacing:-.02em; }
.hero { border:1px solid #294154; border-radius:20px; padding:24px 28px; background:linear-gradient(112deg,rgba(16,42,57,.96),rgba(10,20,31,.94) 62%,rgba(11,25,36,.96)); position:relative; overflow:hidden; box-shadow:0 18px 55px rgba(0,0,0,.17); }
.hero-layout { display:grid; grid-template-columns:minmax(0,1fr) 190px; gap:22px; align-items:center; }
.hero-copy { position:relative; z-index:1; }
.hero-topline { display:flex; align-items:center; gap:9px; color:#9fb2c4; font-size:.78rem; font-weight:600; }
.live-dot { width:8px; height:8px; border-radius:50%; background:var(--cyan); box-shadow:0 0 0 4px rgba(82,224,209,.12),0 0 14px rgba(82,224,209,.8); animation:live-pulse 1.8s ease-in-out infinite; }
.hero h1 { margin:.55rem 0 .45rem; font-size:2.25rem; line-height:1.2; font-weight:700; }
.hero h1 .brand-word { color:var(--cyan); font-size:2.55rem; }
.hero p { margin:0; color:#aebdce; max-width:680px; font-size:1rem; line-height:1.8; }
.hero-meta { display:flex; flex-wrap:wrap; gap:8px; margin-top:15px; }
.hero-meta span { border:1px solid rgba(93,132,157,.35); background:rgba(9,20,30,.55); border-radius:99px; color:#b7c8d8; padding:5px 10px; font-size:.74rem; }
.hero-visual { height:164px; display:grid; place-items:center; position:relative; }
.radar { width:142px; height:142px; position:relative; overflow:hidden; border-radius:50%; border:1px solid rgba(82,224,209,.42); background:radial-gradient(circle,rgba(82,224,209,.13) 0 2px,transparent 3px),repeating-radial-gradient(circle,transparent 0 21px,rgba(82,224,209,.16) 22px 23px),linear-gradient(90deg,transparent 49.5%,rgba(82,224,209,.14) 50%,transparent 50.5%),linear-gradient(0deg,transparent 49.5%,rgba(82,224,209,.14) 50%,transparent 50.5%); box-shadow:0 0 38px rgba(82,224,209,.12),inset 0 0 25px rgba(82,224,209,.08); }
.radar-sweep { position:absolute; inset:0; border-radius:50%; background:conic-gradient(from 0deg,transparent 0 78%,rgba(82,224,209,.02) 83%,rgba(82,224,209,.28) 100%); animation:radar-rotate 5s linear infinite; }
.radar-center { position:absolute; width:7px; height:7px; border-radius:50%; background:#e7fff9; left:calc(50% - 3.5px); top:calc(50% - 3.5px); box-shadow:0 0 15px 5px rgba(82,224,209,.54); }
.radar-contact { position:absolute; width:5px; height:5px; border-radius:50%; background:var(--amber); box-shadow:0 0 9px 2px rgba(255,189,105,.6); animation:contact-blink 2.2s ease-in-out infinite; }
.radar-contact.one { top:29%; left:65%; } .radar-contact.two { top:66%; left:32%; animation-delay:.8s; }
.hero-wave { position:absolute; bottom:0; left:0; width:100%; height:36px; opacity:.42; }
.hero-wave path { fill:none; stroke:var(--cyan); stroke-width:1.5; stroke-dasharray:8 9; animation:wave-flow 7s linear infinite; }
@keyframes radar-rotate { to { transform:rotate(360deg); } }
@keyframes live-pulse { 50% { opacity:.45; box-shadow:0 0 0 7px rgba(82,224,209,.04),0 0 17px rgba(82,224,209,.35); } }
@keyframes contact-blink { 50% { opacity:.3; transform:scale(.7); } }
@keyframes wave-flow { to { stroke-dashoffset:-68; } }
@media (max-width:760px) { .hero-layout { grid-template-columns:1fr 92px; gap:8px; } .radar { width:84px; height:84px; } .hero { padding:18px; } .hero h1 { font-size:1.65rem; } .hero h1 .brand-word { font-size:1.9rem; } .hero p { font-size:.88rem; } .hero-visual { height:105px; } }
@media (prefers-reduced-motion:reduce) { *, *::before, *::after { animation-duration:.01ms !important; animation-iteration-count:1 !important; scroll-behavior:auto !important; } }
.metric { background:linear-gradient(145deg,rgba(17,32,47,.96),rgba(10,18,28,.96)); border:1px solid var(--line); border-radius:14px; padding:14px 16px; min-height:108px; }
.metric-label { color:var(--muted); font-size:.82rem; }
.metric-value { color:var(--ink); font-size:1.75rem; font-weight:700; margin-top:7px; direction:ltr; text-align:right; }
.metric-note { color:#8aa0b6; font-size:.75rem; margin-top:3px; }
.section-kicker { color:var(--cyan); font-size:.8rem; font-weight:700; letter-spacing:.08em; }
.verdict { border:1px solid rgba(255,189,105,.45); background:linear-gradient(135deg,rgba(82,50,20,.3),rgba(16,25,36,.9)); border-radius:14px; padding:16px 19px; }
.mentor-card { border:1px solid rgba(82,224,209,.28); border-radius:14px; padding:14px; margin-top:10px; background:linear-gradient(145deg,rgba(15,38,49,.92),rgba(10,20,31,.96)); box-shadow:inset 0 1px rgba(255,255,255,.025); }
.mentor-head { display:flex; align-items:center; gap:11px; margin-bottom:11px; }
.mentor-avatar { display:grid; place-items:center; width:44px; height:44px; flex:0 0 44px; border:1px solid rgba(82,224,209,.42); border-radius:50%; background:radial-gradient(circle at 35% 28%,rgba(82,224,209,.23),rgba(17,38,51,.96) 72%); color:var(--cyan); font-size:.86rem; font-weight:700; box-shadow:0 0 18px rgba(82,224,209,.11); }
.mentor-name { color:var(--ink); font-weight:700; font-size:.91rem; }
.mentor-role { display:block; color:var(--muted); font-size:.71rem; margin-top:2px; }
.mentor-note { color:#c7d5e2; line-height:1.8; font-size:.84rem; margin:0; }
.mentor-disclaimer { color:#8195a8; font-size:.68rem; margin-top:9px; }
[data-testid="stTabs"] button { font-weight:600; }
[data-testid="stSlider"] [data-baseweb="slider"] { padding-top:.4rem; }
div[data-testid="stPlotlyChart"] { border:1px solid rgba(54,76,97,.72); border-radius:14px; overflow:hidden; background:rgba(9,17,27,.72); }
.stButton>button, [data-testid="stDownloadButton"] button { border-radius:10px; font-weight:600; }
small, .muted { color:var(--muted); }
</style>
""", unsafe_allow_html=True)

SUSPECTS = ["الشبح", "الغايب", "المرتجف", "الظل"]

st.sidebar.markdown("## 📡 طيف — TAYF")
st.sidebar.caption("مختبر محاكاة وتحقيق لاسلكي — كل شيء هنا بيانات تعليمية مصطنعة")
st.sidebar.markdown("---")
st.sidebar.markdown("### إعداد مسرح الإشارة")
suspect = st.sidebar.selectbox("سبب الحادث", SUSPECTS, index=0, help="غيّر المشتبه به وشاهد أثره فوراً على القياسات.")
frequency = st.sidebar.slider("التردد الحامل (MHz)", 400, 6000, 2400, 100)
distance_m = st.sidebar.slider("المسافة (متر)", 10, 1000, 100, 10)
tx_power = st.sidebar.slider("قدرة الإرسال (dBm)", -10, 30, 20, 1)
noise_floor = st.sidebar.slider("أرضية الضوضاء (dBm)", -110, -70, -95, 1)
severity_pct = st.sidebar.slider("شدة الحادث", 0, 100, 100, 5, format="%d%%")
seed = st.sidebar.number_input("بذرة العشوائية", min_value=0, max_value=999999, value=42, step=1, help="ثبّت البذرة لإعادة نفس القياسات أو غيّرها لتوليد أثر ضوضاء مختلف.")
st.sidebar.markdown("---")
st.sidebar.caption("عدّل أي منزلق؛ تتحدث النتائج مباشرة من دون زر تشغيل أو إعادة تحميل يدوية.")
st.sidebar.caption("لا يتصل التطبيق بأي شبكة حقيقية ولا يرسل أو يستقبل حزم Wi-Fi.")

params = LinkParams(
    tx_power_dbm=float(tx_power),
    tx_gain_dbi=2.0,
    rx_gain_dbi=2.0,
    freq_mhz=float(frequency),
    dist_km=float(distance_m) / 1000.0,
    noise_dbm=float(noise_floor),
)
df = run_simulation(suspect, params, seed=int(seed), severity=float(severity_pct) / 100.0)
stats = compare_phases(df)
verdict_data = rank_suspects(df)
incident_rows = df[df["phase"] == "حادث"]

st.markdown(f"""
<div class="hero">
  <div class="hero-layout">
    <div class="hero-copy">
      <div class="hero-topline"><span class="live-dot"></span><span>مختبر مراقبة وتحليل الإشارات</span><span>·</span><span>محاكاة مباشرة</span></div>
      <h1><span class="brand-word">طيف</span> <span style="color:#d9e4ee">/ غرفة التحقيق</span></h1>
      <p>اتبع أثر الإشارة من لحظة استقرارها إلى وقوع الحادث. عدّل خصائص الرابط، راقب التغيّر، ثم اجمع القرائن لتعرف السبب.</p>
      <div class="hero-meta"><span>القناة {frequency:,} MHz</span><span>المسافة {distance_m} m</span><span>المشتبه: {suspect}</span><span>شدة {severity_pct}%</span></div>
    </div>
    <div class="hero-visual" aria-hidden="true"><div class="radar"><div class="radar-sweep"></div><div class="radar-center"></div><div class="radar-contact one"></div><div class="radar-contact two"></div></div></div>
  </div>
  <svg class="hero-wave" viewBox="0 0 1200 36" preserveAspectRatio="none" aria-hidden="true"><path d="M0 20h120l8-2 7 4 12-2h45l8-12 8 25 10-16 8 5h95l8-2 6 3h65l8-17 8 27 10-14 8 4h118l8-2 7 4h112l8-10 8 17 10-9h126l8-2 7 3h170"/></svg>
</div>
""", unsafe_allow_html=True)
st.write("")
current_step = st.slider("حرّك المؤشر الزمني داخل المحاكاة", 0, len(df) - 1, 25, 1, help="اسحب المؤشر لاستكشاف القياسات لحظة بلحظة.")
current = df.iloc[current_step]

k1, k2, k3, k4 = st.columns(4)
def metric_card(col, label: str, value: str, note: str):
    col.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)
metric_card(k1, "قوة الإشارة RSSI", f"{current['rssi_dbm']:.1f} dBm", "القياس عند اللحظة المحددة")
metric_card(k2, "نسبة الإشارة إلى الضوضاء", f"{current['snr_db']:.1f} dB", "SNR عند اللحظة المحددة")
metric_card(k3, "فقدان الحزم", f"{current['packet_loss_pct']:.1f}%", "تقدير تعليمي من SNR")
metric_card(k4, "درجة الحادث", f"{severity_pct}%", f"المشتبه المختار: {suspect}")
st.write("")

pages = st.tabs(["📡 غرفة العمليات", "🌐 خريطة التغطية", "🔭 مختبر QPSK و BER", "⚖️ ملف الأدلة", "📄 التقرير"])
with pages[0]:
    left, right = st.columns([1.7, 1])
    with left:
        st.markdown('<div class="section-kicker">SIGNAL TRACE / RSSI + SNR</div>', unsafe_allow_html=True)
        st.subheader("نبض الرابط عبر الزمن")
        fig = create_interactive_heartbeat(df, current_step=current_step)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "scrollZoom": True, "displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})
        st.caption("ظلّل المنطقة للتكبير، اسحب شريط الزمن أسفل المخطط، أو مرّر المؤشر على الخط لقراءة القيم. الشريط الأحمر الفاتح يحدد فترة الحادث.")
    with right:
        st.markdown('<div class="section-kicker">CASE STATUS</div>', unsafe_allow_html=True)
        st.subheader("حالة مسرح الإشارة")
        if current["phase"] == "حادث":
            st.error(f"الحادث نشط عند t = {current['timestamp_s']:.0f} ثانية")
        else:
            st.success(f"الرابط في المرحلة الأساسية عند t = {current['timestamp_s']:.0f} ثانية")
        st.markdown(f"**المشتبه الحالي:** {suspect}")
        st.markdown(f"**التشخيص الأولي:** {verdict_data['verdict']} · تطابق الأدلة {verdict_data['confidence']}%")
        st.progress(float(current["packet_loss_pct"]) / 100.0, text="مؤشر فقدان الحزم")
        st.markdown("##### تغيّر المرحلة")
        phase_col1, phase_col2 = st.columns(2)
        phase_col1.metric("تغيّر RSSI", f"{stats['rssi_dbm']['delta']:+.1f} dB", help="المتوسط أثناء الحادث ناقص المتوسط الأساسي")
        phase_col2.metric("تغيّر SNR", f"{stats['snr_db']['delta']:+.1f} dB")
        st.markdown('<div class="verdict"><b>مهم:</b> التشخيص قاعدة تعليمية شفافة، وليس قياساً من شبكة فعلية.</div>', unsafe_allow_html=True)
        st.markdown("##### المشرف د. محمد")
        show_doctor_model = st.toggle("إظهار المجسم ثلاثي الأبعاد", value=True, key="show_doctor_model")
        if show_doctor_model:
            components.iframe("/app/static/doctor_character/index.html", height=300, scrolling=False)
        st.session_state.setdefault("mentor_hint_level", 0)
        mentor_text = mentor_guidance(
            phase=str(current["phase"]),
            rssi_delta=float(stats["rssi_dbm"]["delta"]),
            snr_delta=float(stats["snr_db"]["delta"]),
            rssi_std_ratio=float(stats["rssi_dbm"]["std_ratio"]),
            hint_level=int(st.session_state["mentor_hint_level"]),
        )
        st.markdown(
            f'<div class="mentor-card"><div class="mentor-head"><div class="mentor-avatar">د.م</div>'
            f'<div><div class="mentor-name">د. محمد</div><span class="mentor-role">مشرف المختبر · مرشد تعليمي</span></div></div>'
            f'<p class="mentor-note">{mentor_text}</p><div class="mentor-disclaimer">التوجيه مبني على بيانات المحاكاة الحالية، ولا يكشف التشخيص مباشرة.</div></div>',
            unsafe_allow_html=True,
        )
        if st.button("تلميح آخر للمحقق", key="mentor_next_hint", use_container_width=True):
            st.session_state["mentor_hint_level"] = (int(st.session_state["mentor_hint_level"]) + 1) % 3
            st.rerun()

with pages[1]:
    st.markdown('<div class="section-kicker">PROPAGATION FIELD</div>', unsafe_allow_html=True)
    st.subheader("استكشف المجال المكاني للرابط اللاسلكي")
    map_controls = st.columns([1, 1.35])
    with map_controls[0]:
        view_mode = st.radio("طريقة العرض", ["2D الخريطة الرادارية", "3D المجسم الطيفي"], horizontal=True)
    with map_controls[1]:
        map_layer = st.radio("طبقة القياس", ["RSSI · قوة الإشارة", "SNR · جودة الرابط"], horizontal=True)
    map_severity = float(severity_pct) / 100.0
    map_metric = "SNR" if map_layer.startswith("SNR") else "RSSI"
    fig_map = create_rich_heatmap(params, suspect=suspect, incident_t=map_severity, view_mode=view_mode, metric=map_metric)
    st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": True, "scrollZoom": True, "displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})
    st.caption("طبقة RSSI تعرض القدرة المستقبلة، وطبقة SNR تعرض أثر الضوضاء والتداخل على جودة الرابط. اسحب المجسم لتدويره أو حرّك المؤشر فوق الخريطة لقراءة القياس المكاني.")

with pages[2]:
    st.markdown('<div class="section-kicker">MODULATION LAB</div>', unsafe_allow_html=True)
    st.subheader("غيّر الضوضاء وشاهد الرموز تتشتت")
    c1, c2 = st.columns([1, 1])
    with c1:
        noise_amp = st.slider("مضخم الضوضاء المضاف للكوكبة", 0.2, 3.0, 1.0, 0.1)
    with c2:
        n_symbols = st.slider("عدد الرموز المعروضة", 100, 1000, 450, 50)
    baseline_snr = float(df[df["phase"] == "أساسي"]["snr_db"].mean())
    incident_snr = float(incident_rows["snr_db"].mean())
    q1, q2 = st.columns(2)
    with q1:
        st.markdown("#### قبل الحادث")
        st.plotly_chart(create_rich_constellation(baseline_snr, n_symbols=n_symbols, live_noise_amp=1.0, seed=int(seed)), use_container_width=True, config={"displayModeBar": True})
    with q2:
        st.markdown("#### أثناء الحادث")
        st.plotly_chart(create_rich_constellation(incident_snr, n_symbols=n_symbols, live_noise_amp=noise_amp, seed=int(seed) + 1), use_container_width=True, config={"displayModeBar": True})
    st.markdown("#### ميزان أخطاء البت BER")
    st.plotly_chart(create_interactive_ber(current_snr=incident_snr, baseline_snr=baseline_snr), use_container_width=True, config={"displayModeBar": True})

with pages[3]:
    st.markdown('<div class="section-kicker">EVIDENCE BOARD</div>', unsafe_allow_html=True)
    st.subheader("كيف استنتج النظام السبب؟")
    e1, e2 = st.columns([1.1, 1])
    with e1:
        for item in verdict_data["evidence"]:
            st.markdown(f"- **{item['emoji']} {item['text']}** — الدلالة: يدعم {item['supports']}")
        st.markdown("#### مقارنة قبل الحادث وأثناءه")
        comparison = pd.DataFrame([
            {"المقياس": "RSSI (dBm)", "قبل الحادث": stats["rssi_dbm"]["baseline_mean"], "أثناء الحادث": stats["rssi_dbm"]["incident_mean"], "التغير": stats["rssi_dbm"]["delta"]},
            {"المقياس": "SNR (dB)", "قبل الحادث": stats["snr_db"]["baseline_mean"], "أثناء الحادث": stats["snr_db"]["incident_mean"], "التغير": stats["snr_db"]["delta"]},
        ])
        st.dataframe(comparison, use_container_width=True, hide_index=True)
    with e2:
        verdict = verdict_data["verdict"]
        st.markdown(f'<div class="verdict"><div class="section-kicker">MOST LIKELY CAUSE</div><h2>{verdict}</h2><p>درجة مطابقة الأدلة: <b>{verdict_data["confidence"]}%</b></p></div>', unsafe_allow_html=True)
        scores = pd.DataFrame(verdict_data["ranked"], columns=["المشتبه", "درجة المطابقة %"])
        st.bar_chart(scores.set_index("المشتبه"), horizontal=True, height=250, color="#52e0d1")
        metrics_spider = {
            "power_drop": abs(min(0.0, stats["rssi_dbm"]["delta"])) / 25.0,
            "snr_drop": abs(min(0.0, stats["snr_db"]["delta"])) / 25.0,
            "fluctuation": min(1.0, max(0.0, (stats["rssi_dbm"]["std_ratio"] - 1.0) / 8.0)),
            "drift": abs(min(0.0, stats["rssi_slope"])) / 0.8,
            "packet_loss": stats["packet_loss_pct"]["incident_mean"] / 100.0,
        }
        st.plotly_chart(create_interactive_radar(metrics_spider, suspect_name=verdict), use_container_width=True, config={"displayModeBar": True})

with pages[4]:
    st.markdown('<div class="section-kicker">CASE REPORT</div>', unsafe_allow_html=True)
    st.subheader("ملف القضية الحالي")
    report_text = generate_case_summary_text(df, verdict_data)
    st.text_area("التقرير النصي", report_text, height=300)
    d1, d2 = st.columns(2)
    with d1:
        st.download_button("تنزيل التقرير النصي", report_text, file_name="TAYF_case_report.txt", mime="text/plain", use_container_width=True)
    with d2:
        st.download_button("تنزيل القياسات CSV", export_dataframe_csv(df), file_name="TAYF_signal_measurements.csv", mime="text/csv", use_container_width=True)
