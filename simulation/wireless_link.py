"""
طيف — TAYF
نموذج الرابط اللاسلكي الأساسي والمعادلات
"""
import numpy as np

# ثوابت فيزيائية
SPEED_OF_LIGHT = 3e8  # m/s


def wavelength(freq_hz: float) -> float:
    """λ = c / f"""
    return SPEED_OF_LIGHT / freq_hz


def fspl_db(freq_mhz: float, dist_km: float) -> float:
    """
    خسارة المسار في الفضاء الحر (Free-Space Path Loss)
    FSPL(dB) = 32.44 + 20·log10(f_MHz) + 20·log10(d_km)
    """
    if dist_km <= 0:
        return 0.0
    return 32.44 + 20 * np.log10(freq_mhz) + 20 * np.log10(dist_km)


def received_power_dbm(
    tx_power_dbm: float,
    tx_gain_dbi: float,
    rx_gain_dbi: float,
    path_loss_db: float,
    extra_loss_db: float = 0.0,
) -> float:
    """
    Pr(dBm) = Pt + Gt + Gr - L
    """
    return tx_power_dbm + tx_gain_dbi + rx_gain_dbi - path_loss_db - extra_loss_db


def snr_db(signal_dbm: float, noise_dbm: float) -> float:
    """SNR(dB) = P_signal - P_noise  (في الـ dBm)"""
    return signal_dbm - noise_dbm


def doppler_shift_hz(speed_mps: float, freq_hz: float, angle_deg: float) -> float:
    """
    fD = (v / λ) · cos(θ)
    angle_deg: زاوية الحركة بالنسبة لاتجاه الإشارة
    """
    lam = wavelength(freq_hz)
    theta = np.radians(angle_deg)
    return (speed_mps / lam) * np.cos(theta)


def thermal_noise_dbm(bandwidth_hz: float, noise_figure_db: float = 7.0) -> float:
    """
    ضوضاء حرارية:  N = kTB  (بالـ dBm) + noise figure
    k = 1.38e-23 J/K, T = 290 K
    """
    k = 1.38e-23
    T = 290
    noise_w = k * T * bandwidth_hz
    noise_dbm = 10 * np.log10(noise_w / 1e-3)
    return noise_dbm + noise_figure_db


def packet_loss_from_snr(snr_db_val: float, threshold_db: float = 10.0) -> float:
    """
    نموذج مبسّط: كلما وقع SNR تحت العتبة، زادت نسبة فقدان الحزم
    """
    if snr_db_val >= threshold_db:
        return max(0.0, (threshold_db - snr_db_val) * 0.1 + np.random.uniform(0, 2))
    deficit = threshold_db - snr_db_val
    loss = min(100.0, deficit * 8 + np.random.uniform(0, 5))
    return max(0.0, loss)


def ber_qpsk(snr_linear: float) -> float:
    """
    BER لـ QPSK: BER = Q(sqrt(2·SNR))
    Q(x) ≈ 0.5 · erfc(x / sqrt(2))
    """
    from scipy.special import erfc
    if snr_linear <= 0:
        return 0.5
    arg = np.sqrt(2 * snr_linear)
    return 0.5 * erfc(arg / np.sqrt(2))

