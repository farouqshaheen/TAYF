"""طيف — مختبر تفاعلي لمحاكاة التحقيق في الروابط اللاسلكية."""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from analysis.diagnosis import rank_suspects
from analysis.metrics import compare_phases
from reporting.report_generator import export_dataframe_csv, generate_case_summary_text
from simulation.data_generator import run_simulation
from simulation.scenarios import LinkParams
from visualization.interactive_ber import create_interactive_ber
from visualization.interactive_constellation import create_rich_constellation
from visualization.interactive_heatmap import create_rich_heatmap
from visualization.interactive_oscilloscope import create_interactive_heartbeat
from visualization.interactive_radar import create_interactive_radar

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
.hero { border:1px solid #294154; border-radius:18px; padding:22px 26px; background:linear-gradient(115deg,rgba(16,42,57,.92),rgba(10,20,31,.86)); position:relative; overflow:hidden; }
.hero:after { content:''; position:absolute; left:-35px; top:-65px; width:210px; height:210px; border:1px solid rgba(82,224,209,.18); border-radius:50%; box-shadow:0 0 0 24px rgba(82,224,209,.035),0 0 0 50px rgba(82,224,209,.025); }
.eyebrow { color:var(--cyan); font-size:.82rem; letter-spacing:.12em; font-weight:700; }
.hero h1 { margin:.3rem 0 .35rem; font-size:2rem; }
.hero p { margin:0; color:#aebdce; max-width:760px; }
.metric { background:linear-gradient(145deg,rgba(17,32,47,.96),rgba(10,18,28,.96)); border:1px solid var(--line); border-radius:14px; padding:14px 16px; min-height:108px; }
.metric-label { color:var(--muted); font-size:.82rem; }
.metric-value { color:var(--ink); font-size:1.75rem; font-weight:700; margin-top:7px; direction:ltr; text-align:right; }
.metric-note { color:#8aa0b6; font-size:.75rem; margin-top:3px; }
.section-kicker { color:var(--cyan); font-size:.8rem; font-weight:700; letter-spacing:.08em; }
.verdict { border:1px solid rgba(255,189,105,.45); background:linear-gradient(135deg,rgba(82,50,20,.3),rgba(16,25,36,.9)); border-radius:14px; padding:16px 19px; }
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
current_step = st.slider("حرّك المؤشر الزمني داخل المحاكاة", 0, len(df) - 1, 25, 1, help="اسحب المؤشر لاستكشاف القياسات لحظة بلحظة.")
current = df.iloc[current_step]

st.markdown("""
<div class="hero">
  <div class="eyebrow">WIRELESS FORENSICS · INTERACTIVE SIMULATION</div>
  <h1>طيف | غرفة التحقيق اللاسلكي</h1>
  <p>غيّر خصائص الرابط من اللوحة الجانبية، راقب لحظة وقوع الحادث، ثم تتبّع الأدلة التي قادت إلى التشخيص.</p>
</div>
""", unsafe_allow_html=True)
st.write("")

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
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "scrollZoom": True})
        st.caption("اسحب داخل المخطط للتكبير، مرّر المؤشر على النقاط لقراءة القياسات، أو استخدم منزلق الزمن أعلاه.")
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

with pages[1]:
    st.markdown('<div class="section-kicker">PROPAGATION FIELD</div>', unsafe_allow_html=True)
    st.subheader("استكشف توزيع القدرة حول المرسل")
    view_mode = st.radio("طريقة الاستكشاف", ["2D الخريطة الرادارية", "3D المجسم الطيفي"], horizontal=True)
    map_severity = float(severity_pct) / 100.0
    fig_map = create_rich_heatmap(params, suspect=suspect, incident_t=map_severity, view_mode=view_mode)
    st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": True, "scrollZoom": True})
    st.caption("في وضع 3D اسحب لتدوير السطح واستخدم التكبير لاستكشاف مناطق التغطية. حرّك إعدادات الرابط من اللوحة الجانبية لتحديث الخريطة.")

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
