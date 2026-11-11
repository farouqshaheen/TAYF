import numpy as np
import pandas as pd
from simulation.wireless_link import wavelength, fspl_db, received_power_dbm, snr_db
from simulation.scenarios import LinkParams
from simulation.data_generator import run_simulation
from analysis.metrics import compare_phases
from analysis.diagnosis import rank_suspects

def test_physics_equations():
    # اختبار طول الموجة لـ 3 GHz: c / f = 3e8 / 3e9 = 0.1 m
    lam = wavelength(3e9)
    assert np.isclose(lam, 0.1)

    # اختبار FSPL لتردد 900 MHz ومسافة 1 كم
    # FSPL = 32.44 + 20*log10(900) + 20*log10(1) = 32.44 + 59.08 = 91.52 dB
    pl = fspl_db(900, 1.0)
    assert np.isclose(pl, 91.52, atol=0.1)

def test_interference_suspect():
    params = LinkParams()
    df = run_simulation("الشبح", params, seed=42)
    stats = compare_phases(df)
    
    # في حالة الشبح، يجب أن ينخفض SNR بشكل ملحوظ بينما يبقى RSSI قريباً من مستواه
    assert stats["snr_db"]["delta"] < -5
    assert abs(stats["rssi_dbm"]["delta"]) < 5
    
    # محرك التشخيص يجب أن يتهم الشبح
    verdict = rank_suspects(df)
    assert verdict["verdict"] == "الشبح"

def test_path_loss_suspect():
    params = LinkParams()
    df = run_simulation("الغايب", params, seed=42)
    verdict = rank_suspects(df)
    assert verdict["verdict"] == "الغايب"

def test_fast_fading_suspect():
    params = LinkParams()
    df = run_simulation("المرتجف", params, seed=42)
    stats = compare_phases(df)
    # الانحراف المعياري للـ RSSI يجب أن يتضاعف عدة مرات
    assert stats["rssi_dbm"]["std_ratio"] > 3.0
    verdict = rank_suspects(df)
    assert verdict["verdict"] == "المرتجف"

