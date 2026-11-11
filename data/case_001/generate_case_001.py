"""
طيف — TAYF
توليد وحفظ بيانات الحالة 001 المسبقة للعرض الحي
"""
from simulation.scenarios import LinkParams
from simulation.data_generator import run_simulation
import os

def generate_and_save_case_001():
    out_dir = os.path.dirname(__file__)
    csv_path = os.path.join(out_dir, "case_001_data.csv")

    params = LinkParams(
        tx_power_dbm=20.0,
        tx_gain_dbi=2.0,
        rx_gain_dbi=2.0,
        freq_mhz=2400.0,
        dist_km=0.08,
        noise_dbm=-95.0
    )
    # الحالة 001 هي سيناريو الشبح (التداخل)
    df = run_simulation(suspect="الشبح", params=params, seed=101)
    df.to_csv(csv_path, index=False)
    print(f"Case 001 data saved to {csv_path}")

if __name__ == "__main__":
    generate_and_save_case_001()

