"""
فحص وتدقيق شامل لجميع أجزاء مشروع طيف
"""
import os
import sys

# ضمان مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.wireless_link import (
    wavelength, fspl_db, received_power_dbm, snr_db,
    doppler_shift_hz, thermal_noise_dbm, packet_loss_from_snr, ber_qpsk
)
from simulation.scenarios import LinkParams, apply_suspect, SUSPECTS
from simulation.data_generator import run_simulation
from analysis.metrics import compare_phases
from analysis.evidence import extract_evidence
from analysis.diagnosis import rank_suspects
from visualization.oscilloscope import plot_heartbeat
from visualization.heatmap import plot_heatmap
from visualization.constellation import plot_constellation
from visualization.ber_curve import plot_ber_curve
from visualization.fingerprint import plot_fingerprint
from reporting.report_generator import generate_case_summary_text, export_dataframe_csv

def run_audit():
    print("==================================================")
    print("      📡 بدء الفحص والتدقيق الشامل لنظام طيف       ")
    print("==================================================")

    # 1. اختبار الحسابات الفيزيائية
    print("\n[1] فحص دقة المعادلات الفيزيائية:")
    lam = wavelength(2.4e9)
    print(f"  • طول الموجة لـ 2.4 GHz: {lam:.4f} m (المتوقع: 0.1250 m)")
    assert abs(lam - 0.125) < 1e-4

    pl = fspl_db(2400.0, 0.1)  # 100 متر على 2.4 GHz
    print(f"  • خسارة المسار FSPL عند 100m: {pl:.2f} dB")
    assert pl > 70 and pl < 90

    # 2. اختبار المشتبه بهم الأربعة
    print("\n[2] فحص دقة المحاكاة والتشخيص للمشتبه بهم الأربعة:")
    params = LinkParams()
    
    for s_name in ["الغايب", "الشبح", "المرتجف", "الظل"]:
        df = run_simulation(s_name, params, seed=42)
        assert len(df) == 50, f"عدد العينات غير صحيح: {len(df)}"
        
        stats = compare_phases(df)
        verdict = rank_suspects(df)
        
        v_name = verdict["verdict"]
        conf = verdict["confidence"]
        
        is_pass = (v_name == s_name)
        status_sym = "✅ نجاح" if is_pass else "❌ فشل"
        print(f"  • السيناريو: [{s_name:<8}] ➔ الحكم: [{v_name:<8}] ({conf:>3}%) ➔ {status_sym}")
        
        if not is_pass:
            print(f"    [تنبيه] الأدلة المستخرجة: {verdict['evidence']}")
            print(f"    [تنبيه] الإحصاءات: RSSI delta={stats['rssi_dbm']['delta']}, SNR delta={stats['snr_db']['delta']}, Std ratio={stats['rssi_dbm']['std_ratio']}, slope={stats['rssi_slope']}")
        
        assert is_pass, f"فشل تشخيص {s_name}!"

    # 3. اختبار كل الدوال المرئية (Visualizations)
    print("\n[3] فحص توليد المخططات البيانية والريندر:")
    df_sample = run_simulation("الشبح", params, seed=42)
    stats_sample = compare_phases(df_sample)
    
    fig1 = plot_heartbeat(df_sample)
    print("  • راسم الذبذبات (نبضة القلب): تم بنجاح")
    
    fig2 = plot_heatmap(params, suspect="الشبح", incident_t=0.8)
    print("  • خريطة التغطية الحرارية: تم بنجاح")
    
    fig3 = plot_constellation(snr_db=stats_sample["snr_db"]["incident_mean"])
    print("  • كوكبة QPSK (بصمة الجريمة): تم بنجاح")
    
    fig4 = plot_ber_curve(current_snr=stats_sample["snr_db"]["incident_mean"], baseline_snr=stats_sample["snr_db"]["baseline_mean"])
    print("  • منحنى BER (ميزان الجريمة): تم بنجاح")
    
    fig5 = plot_fingerprint({
        "power_drop": 0.2, "snr_drop": 0.8, "fluctuation": 0.1, "drift": 0.1, "packet_loss": 0.5
    }, suspect_name="الشبح")
    print("  • بصمة الجريمة (Spider Radar): تم بنجاح")

    # 4. فحص التقارير
    print("\n[4] فحص إنشاء التقارير وتصدير CSV:")
    v_data = rank_suspects(df_sample)
    rep_text = generate_case_summary_text(df_sample, v_data)
    assert len(rep_text) > 200
    print("  • وثيقة التقرير الجنائي: متكاملة")
    
    csv_str = export_dataframe_csv(df_sample)
    assert len(csv_str) > 500
    print("  • سجل قياسات CSV: سليم")

    print("\n==================================================")
    print("  🎉 نتيجة الفحص: النظام خالٍ من الأخطاء وجاهز 100%! ")
    print("==================================================")

if __name__ == "__main__":
    run_audit()

