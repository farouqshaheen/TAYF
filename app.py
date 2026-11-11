"""
طيف — TAYF
تطبيق غرفة التحقيق الجنائي في الإشارات اللاسلكية — النسخة التفاعلية والحركية الشاملة
تم التخلص نهائياً من أي صور ثابتة، واستبدالها بمجسمات ومخططات Plotly + Canvas تفاعلية وحركية
"""
import streamlit as st
import numpy as np
import pandas as pd
import time
import os
import sys

# ضمان مسار المشروع
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from simulation.scenarios import LinkParams, SUSPECTS
from simulation.data_generator import run_simulation
from analysis.metrics import compare_phases
from analysis.evidence import extract_evidence
from analysis.diagnosis import rank_suspects
from visualization.interactive_oscilloscope import create_interactive_heartbeat
from visualization.cinematic_heartbeat import get_cinematic_ecg_html
from visualization.interactive_heatmap import create_rich_heatmap
from visualization.interactive_constellation import create_rich_constellation
from visualization.interactive_ber import create_interactive_ber
from visualization.interactive_radar import create_interactive_radar
from reporting.report_generator import generate_case_summary_text, export_dataframe_csv
import streamlit.components.v1 as components

# إعداد الصفحة وتصميم الـ Dark Cyber / Forensics
st.set_page_config(
    page_title="طيف | مختبر التحقيق الجنائي اللاسلكي",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS بطابع أمني عربي داكن نيون احترافي
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .stApp {
        background-color: #050b14;
        color: #c5c6c7;
    }
    
    .stSidebar {
        background-color: #0b111e;
        border-left: 1px solid #162032;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #0d1527 0%, #050b14 100%);
        border: 1px solid rgba(0, 240, 255, 0.3);
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.6);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: #00f0ff;
    }
    
    .verdict-box {
        background: radial-gradient(circle, #2a0808 0%, #0d0202 100%);
        border: 2px solid #ff1744;
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        margin-top: 15px;
        box-shadow: 0 0 25px rgba(255, 23, 68, 0.5);
    }

    .evidence-badge {
        background-color: #0d1527;
        border-right: 4px solid #ff1744;
        padding: 12px 18px;
        margin-bottom: 10px;
        border-radius: 6px;
        font-size: 1.05rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }

    /* أزرار تفاعلية فخمة */
    .stButton>button {
        font-family: 'Tajawal', sans-serif;
        font-weight: 700;
        border-radius: 8px;
        transition: all 0.25s ease;
    }
</style>
""", unsafe_allow_html=True)

# تهيئة الـ Session State
if "df_sim" not in st.session_state:
    st.session_state.df_sim = None
if "current_suspect" not in st.session_state:
    st.session_state.current_suspect = "الشبح"
if "mystery_mode" not in st.session_state:
    st.session_state.mystery_mode = False
if "mystery_actual" not in st.session_state:
    st.session_state.mystery_actual = None

# القائمة الجانبية
st.sidebar.markdown("""
<div style="text-align: center; padding: 10px 0;">
    <h2 style="color: #00f0ff; margin-bottom: 2px;">📡 طيف — TAYF</h2>
    <p style="color: #94a3b8; font-size: 0.85rem;">مختبر التحقيق الجنائي في الإشارات</p>
</div>
""", unsafe_allow_html=True)

tool_page = st.sidebar.radio(
    "أدوات غرفة التحقيق:",
    [
        "🚪 غرفة العمليات (الرئيسية)",
        "📁 ملف الحالة 001 (د. محمد رسمي)",
        "⚙️ محاكي مسرح الترددات",
        "📡 راسم الذبذبات الحي (Live ECG)",
        "🌡️ خريطة التغطية اللاسلكية (2D / 3D)",
        "🔭 كوكبة QPSK التفاعلية",
        "📈 ميزان الجريمة (BER)",
        "⚖️ لوحة الأدلة وحكم المحقق",
        "📄 تقرير القضية الرسمي"
    ]
)

# معلمات الرابط الافتراضية
default_params = LinkParams(
    tx_power_dbm=20.0,
    tx_gain_dbi=2.0,
    rx_gain_dbi=2.0,
    freq_mhz=2400.0,
    dist_km=0.1,
    noise_dbm=-95.0
)

# التأكد من وجود بيانات محاكاة
if st.session_state.df_sim is None:
    st.session_state.df_sim = run_simulation("الشبح", default_params, seed=101)

df = st.session_state.df_sim

# ========================================================
# 1. غرفة العمليات الرئيسية
# ========================================================
if tool_page == "🚪 غرفة العمليات (الرئيسية)":
    st.title("📡 طيف — مختبر التحقيق الجنائي في الإشارات اللاسلكية")
    st.markdown("""
    > **القضية باختصار:** إشارة لاسلكية اتقتلت وتدهورت جودتها بشكل مباغت في مسرح الاتصال. 
    > مهمتك كمحقق هي جمع القرائن الفيزيائية ومعرفة **مين قتل الإشارة؟**
    """)
    
    st.write("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color:#66bb6a;">🌑 الغايب</h3>
            <p><strong>Path Loss</strong></p>
            <small>المستقبل بعد والمسافة ضيعت الإشارة</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color:#ff5252;">👻 الشبح</h3>
            <p><strong>Interference</strong></p>
            <small>الإشارة موجودة بس في ضوضاء خنقتها</small>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color:#ffd740;">⚡ المرتجف</h3>
            <p><strong>Fast Fading</strong></p>
            <small>انعكاسات ومسارات متعددة خلتها ترتجف</small>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color:#40c4ff;">🌫️ الظل</h3>
            <p><strong>Slow Fading</strong></p>
            <small>عائق وتظليل نزل المتوسط تدريجياً</small>
        </div>
        """, unsafe_allow_html=True)

    st.write("---")
    st.subheader("⚡ الإجراء السريع للمحقق:")
    q_col1, q_col2 = st.columns(2)
    with q_col1:
        if st.button("🚨 تشغيل قضية د. محمد رسمي موسى (الحالة 001)", use_container_width=True, type="primary"):
            st.session_state.df_sim = run_simulation("الشبح", default_params, seed=101)
            st.session_state.current_suspect = "الشبح"
            st.session_state.mystery_mode = False
            st.success("تم شحن مسرح الجريمة ببيانات شبكة الحالة 001! توجه لراسم الذبذبات أو لوحة الأدلة.")
    with q_col2:
        if st.button("🎲 وضع الغموض (تحدي الدكتور!)", use_container_width=True):
            chosen = np.random.choice(["الغايب", "الشبح", "المرتجف", "الظل"])
            st.session_state.mystery_actual = chosen
            st.session_state.mystery_mode = True
            st.session_state.df_sim = run_simulation(chosen, default_params, seed=np.random.randint(1, 9999))
            st.warning("⚠️ تم إحداث جريمة لاسلكية غامضة! اجمع الأدلة من الأدوات واكتشف القاتل.")

# ========================================================
# 2. ملف الحالة 001
# ========================================================
elif tool_page == "📁 ملف الحالة 001 (د. محمد رسمي)":
    st.title("📁 ملف القضية 001 — شبكة د. محمد رسمي موسى")
    st.info("حالة مخصصة لتقديم العرض التفاعلي أمام الدكتور | جامعة الزرقاء")
    
    st.markdown("""
    ### 📝 البلاغ الجنائي:
    *وصل الدكتور محمد لمكتبه في الصباح، وكانت الشبكة تعمل بكفاءة 100%.*
    *فجأة وبدون مقدمات، انقطعت مكالمات الـ Zoom وبدأ تقطيع مريب بالفيديو، ورغم أن إشارة الواي فاي على الجهاز تُظهر أبراجاً ممتلئة تقريباً، إلا أن البيانات لا تمر!*
    
    **السؤال الجوهري:** إذا كانت الإشارة قوية.. ليش الاتصال ميت؟
    """)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔍 تثبيت بيانات القضية 001 في المختبر", type="primary", use_container_width=True):
            st.session_state.df_sim = run_simulation("الشبح", default_params, seed=101)
            st.session_state.current_suspect = "الشبح"
            st.session_state.mystery_mode = False
            st.success("✅ البيانات جاهزة للفحص في كل شاشات المختبر الآن!")
    with col_btn2:
        if st.button("⚡ إعادة ضبط ومعايرة الشبكة", use_container_width=True):
            st.session_state.df_sim = run_simulation("الشبح", default_params, seed=101)

    if st.session_state.df_sim is not None:
        st.write("---")
        st.subheader("🎬 نبضة قلب شبكة د. محمد (رادار حي 60 FPS):")
        df_target = st.session_state.df_sim
        rssi_list = [float(v) for v in df_target["rssi_dbm"].values]
        snr_list = [float(v) for v in df_target["snr_db"].values]
        is_inc = bool(st.session_state.current_suspect != "طبيعي")
        
        ecg_html = get_cinematic_ecg_html(rssi_list, snr_list, is_incident=is_inc)
        components.html(ecg_html, height=440)
        
        with st.expander("📊 تحليل إحصائي تفاعلي متقدم (Plotly Scope)"):
            fig_inter = create_interactive_heartbeat(st.session_state.df_sim)
            st.plotly_chart(fig_inter, use_container_width=True)

# ========================================================
# 3. محاكي مسرح الترددات
# ========================================================
elif tool_page == "⚙️ محاكي مسرح الترددات":
    st.title("⚙️ محاكي مسرح الترددات (توليد السيناريوهات)")
    
    with st.form("sim_controls"):
        colA, colB, colC = st.columns(3)
        with colA:
            suspect_choice = st.selectbox("المشتبه فيه لتنفيذ الحادث:", ["الشبح", "الغايب", "المرتجف", "الظل"])
            freq = st.number_input("التردد الحامل (MHz):", value=2400.0, step=100.0)
        with colB:
            dist = st.number_input("المسافة الأولية (متر):", value=100.0, step=10.0) / 1000.0
            tx_pow = st.number_input("قدرة الإرسال (dBm):", value=20.0, step=1.0)
        with colC:
            seed_val = st.number_input("البذرة العشوائية (Seed):", value=42, step=1)
            noise_val = st.number_input("ضوضاء الخلفية (dBm):", value=-95.0, step=1.0)

        submitted = st.form_submit_button("💥 إطلاق الحادث وتوليد مسرح الإشارات")
        if submitted:
            custom_params = LinkParams(
                tx_power_dbm=tx_pow,
                freq_mhz=freq,
                dist_km=dist,
                noise_dbm=noise_val
            )
            st.session_state.df_sim = run_simulation(suspect_choice, custom_params, seed=int(seed_val))
            st.session_state.current_suspect = suspect_choice
            st.session_state.mystery_mode = False
            st.success(f"تم تنفيذ حادث 【 {suspect_choice} 】 وتوليد 50 ثانية من القياسات الدقيقة!")

# ========================================================
# 4. راسم الذبذبات الحي
# ========================================================
elif tool_page == "📡 راسم الذبذبات الحي (Live ECG)":
    st.title("📡 راسم الذبذبات الحي — نبضة قلب الإشارة السينمائية")
    st.write("مراقبة حية وتدفق مستمر لسلوك قوة الإشارة (RSSI) مقابل نسبة الضوضاء (SNR) بمعدل 60 إطار بالثانية:")

    rssi_list = [float(v) for v in df["rssi_dbm"].values]
    snr_list = [float(v) for v in df["snr_db"].values]
    is_inc = bool(st.session_state.current_suspect != "طبيعي")
    
    ecg_html = get_cinematic_ecg_html(rssi_list, snr_list, is_incident=is_inc)
    components.html(ecg_html, height=440)

    st.write("---")
    st.subheader("🕹️ محاكي التدفق الزمني التفاعلي:")
    c1, c2, c3 = st.columns([1.2, 1, 2])
    with c1:
        start_anim = st.button("▶️ تشغيل محاكاة التدفق بالثواني", type="primary")
    with c2:
        show_all = st.button("⏹️ عرض السجل الكامل")

    chart_placeholder = st.empty()
    status_placeholder = st.empty()

    if start_anim:
        for step_idx in range(4, len(df), 2):
            fig_anim = create_interactive_heartbeat(df, current_step=step_idx)
            chart_placeholder.plotly_chart(fig_anim, use_container_width=True, key=f"anim_{step_idx}")
            
            curr_row = df.iloc[step_idx]
            is_incident = (curr_row["phase"] == "حادث")
            status_text = "🚨 مسرح الجريمة نشط! انهيار في جودة الإشارة!" if is_incident else "🟢 الرابط يعمل بشكل طبيعي ومستقر"
            status_placeholder.markdown(f"""
            <div style="background-color: {'#330808' if is_incident else '#082613'}; border: 1px solid {'#ff1744' if is_incident else '#00e676'}; border-radius: 8px; padding: 10px; text-align: center;">
                <strong>الثانية: {curr_row['timestamp_s']} ث | الحالة: {status_text} | RSSI: {curr_row['rssi_dbm']:.1f} dBm | SNR: {curr_row['snr_db']:.1f} dB</strong>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.06)
        fig_final = create_interactive_heartbeat(df)
        chart_placeholder.plotly_chart(fig_final, use_container_width=True)
    else:
        fig_static = create_interactive_heartbeat(df)
        chart_placeholder.plotly_chart(fig_static, use_container_width=True)

# ========================================================
# 5. خريطة التغطية اللاسلكية (2D / 3D)
# ========================================================
elif tool_page == "🌡️ خريطة التغطية اللاسلكية (2D / 3D)":
    st.title("🌡️ خريطة مسح التغطية اللاسلكية — 2D & 3D Interactive")
    st.write("توزع مستويات القدرة في الفضاء المحيط بالمرسل بالاعتماد على معادلة الفضاء الحر (FSPL):")
    
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1.5, 1.5, 1])
    with col_ctrl1:
        view_mode = st.radio("نمط العرض المرئي:", ["2D الخريطة الرادارية", "3D المجسم الطيفي"], horizontal=True)
    with col_ctrl2:
        t_val = st.slider("🎚️ تحكم بشدة وزحف الحادث في المكان:", 0.0, 1.0, 0.85, 0.05)
    with col_ctrl3:
        st.metric("شدة الحادث", f"{t_val*100:.0f}%", delta=f"{t_val*20:.1f} dB فقد")

    fig_hm = create_rich_heatmap(default_params, suspect=st.session_state.current_suspect, incident_t=t_val, view_mode=view_mode)
    st.plotly_chart(fig_hm, use_container_width=True)
    st.caption("✨ في نمط 3D، يمكنك تدوير المجسم وتكبيره وتفحصه من أي زاوية بحرية كاملة بالماوس!")

# ========================================================
# 6. كوكبة QPSK التفاعلية
# ========================================================
elif tool_page == "🔭 كوكبة QPSK التفاعلية":
    st.title("🔭 كوكبة QPSK التفاعلية — بصمة الجريمة الحية")
    st.write("كل نقطة تمثل رمزاً مشفراً تم استقباله. انتشار وتشتت النقاط يثبت تشوه الإشارة بواسطة الضوضاء والتداخل:")
    
    col_k1, col_k2 = st.columns([2, 1])
    with col_k1:
        noise_amp = st.slider("🎛️ مضخم الضوضاء الحي (Real-time Noise Injection):", 0.5, 3.0, 1.0, 0.1)
    with col_k2:
        n_syms = st.slider("عدد الرموز المرصودة:", 200, 800, 450, 50)

    inc_snr = df[df["phase"] == "حادث"]["snr_db"].mean()
    base_snr = df[df["phase"] == "أساسي"]["snr_db"].mean()

    col_box1, col_box2 = st.columns(2)
    with col_box1:
        st.subheader("قبل الحادث (طبيعي ومحكم)")
        fig_c1 = create_rich_constellation(base_snr, n_symbols=n_syms, live_noise_amp=1.0)
        st.plotly_chart(fig_c1, use_container_width=True)
    with col_box2:
        st.subheader("أثناء الحادث (تشتت وانهيار الرموز)")
        fig_c2 = create_rich_constellation(inc_snr, n_symbols=n_syms, live_noise_amp=noise_amp)
        st.plotly_chart(fig_c2, use_container_width=True)

# ========================================================
# 7. ميزان الجريمة (BER)
# ========================================================
elif tool_page == "📈 ميزان الجريمة (BER)":
    st.title("📈 ميزان الجريمة — منحنى معدل أخطاء البت (BER)")
    st.write("مقارنة موقع الإشارة الفعلي على منحنى احتمالية الخطأ النظري لـ QPSK:")
    
    base_snr = df[df["phase"] == "أساسي"]["snr_db"].mean()
    inc_snr = df[df["phase"] == "حادث"]["snr_db"].mean()
    
    fig_ber = create_interactive_ber(current_snr=inc_snr, baseline_snr=base_snr)
    st.plotly_chart(fig_ber, use_container_width=True)

# ========================================================
# 8. لوحة الأدلة وحكم المحقق
# ========================================================
elif tool_page == "⚖️ لوحة الأدلة وحكم المحقق":
    st.title("⚖️ لوحة الأدلة وقرار المحقق النهائي")
    
    verdict_data = rank_suspects(df)
    
    col_ev, col_vd = st.columns([1.2, 1])
    
    with col_ev:
        st.subheader("📌 شريط الأدلة والقرائن:")
        for ev in verdict_data["evidence"]:
            st.markdown(f"""
            <div class="evidence-badge">
                <strong>{ev['emoji']} {ev['text']}</strong><br>
                <small style="color: #00f0ff;">الدلالة الفيزيائية: تدعم اتهام المشتبه به 【 {ev['supports']} 】</small>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("---")
        st.subheader("🕸️ بصمة التوقيع الجنائي:")
        stats = compare_phases(df)
        metrics_spider = {
            "power_drop": abs(min(0.0, stats["rssi_dbm"]["delta"])) / 25.0,
            "snr_drop": abs(min(0.0, stats["snr_db"]["delta"])) / 25.0,
            "fluctuation": min(1.0, (stats["rssi_dbm"]["std_ratio"] - 1.0) / 8.0),
            "drift": abs(min(0.0, stats["rssi_slope"])) / 0.8,
            "packet_loss": stats["packet_loss_pct"]["incident_mean"] / 100.0,
        }
        fig_radar = create_interactive_radar(metrics_spider, suspect_name=verdict_data["verdict"])
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_vd:
        st.subheader("⚖️ الحكم الجنائي الصادر:")
        verdict = verdict_data["verdict"]
        conf = verdict_data["confidence"]
        
        st.markdown(f"""
        <div class="verdict-box">
            <h4 style="color: #ff9100; margin-bottom: 5px;">المتهم الأرجح بإعدام الاتصال:</h4>
            <h1 style="color: #ff1744; font-size: 2.8rem; margin: 10px 0;">【 {verdict} 】</h1>
            <p style="font-size: 1.25rem; color: #ffffff;">نسبة اليقين والقرائن: <strong>{conf}%</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        st.write("📋 **ميزان الشبهة بالمجموعة كاملة:**")
        for s_name, s_pct in verdict_data["ranked"]:
            st.write(f"• **{s_name}**: {s_pct}%")
            st.progress(s_pct / 100.0)

        if st.session_state.mystery_mode:
            st.write("---")
            if st.button("🔓 كشف الحقيقة (المجرم الحقيقي في وضع الغموض)", type="primary"):
                actual = st.session_state.mystery_actual
                if actual == verdict:
                    st.balloons()
                    st.success(f"🎯 عبقري! حكمك في محله تماماً! المجرم الحقيقي هو فعلاً: 【 {actual} 】")
                else:
                    st.error(f"المجرم الحقيقي كان: 【 {actual} 】.. لكن القرائن الرياضية كانت خادعة ومتقاربة!")

# ========================================================
# 9. تقرير القضية الرسمي
# ========================================================
elif tool_page == "📄 تقرير القضية الرسمي":
    st.title("📄 ملف التقرير الجنائي المعتمد للقضية")
    
    verdict_data = rank_suspects(df)
    report_text = generate_case_summary_text(df, verdict_data)
    
    st.text_area("نص الوثيقة الرسمية الصادرة عن نظام طيف:", report_text, height=350)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="📥 تحميل تقرير القضية النصي (.txt)",
            data=report_text,
            file_name="TAYF_Forensic_Case_Report.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col_d2:
        csv_data = export_dataframe_csv(df)
        st.download_button(
            label="📊 تحميل سجل القياسات الكامل (.csv)",
            data=csv_data,
            file_name="tayf_signals_telemetry.csv",
            mime="text/csv",
            use_container_width=True
        )
