from analysis.mentor import mentor_guidance


def test_baseline_message_teaches_establishing_reference():
    message = mentor_guidance("أساسي", rssi_delta=0, snr_delta=0, rssi_std_ratio=1)
    assert "خط الأساس" in message
    assert "الحادث" in message


def test_guidance_identifies_snr_drop_with_stable_rssi_without_naming_cause():
    message = mentor_guidance("حادث", rssi_delta=-0.4, snr_delta=-19.7, rssi_std_ratio=1.1)
    assert "SNR" in message
    assert "RSSI" in message
    assert "التشخيص" not in message


def test_guidance_identifies_received_power_drop():
    message = mentor_guidance("حادث", rssi_delta=-14.0, snr_delta=-13.0, rssi_std_ratio=1.2)
    assert "RSSI" in message
    assert "خريطة التغطية" in message


def test_hints_are_sequential_and_relevant_to_incident_phase():
    observation = mentor_guidance("حادث", rssi_delta=-0.4, snr_delta=-19.7, rssi_std_ratio=1.1, hint_level=0)
    map_hint = mentor_guidance("حادث", rssi_delta=-0.4, snr_delta=-19.7, rssi_std_ratio=1.1, hint_level=1)
    next_step = mentor_guidance("حادث", rssi_delta=-0.4, snr_delta=-19.7, rssi_std_ratio=1.1, hint_level=2)

    assert len({observation, map_hint, next_step}) == 3
    assert "خريطة التغطية" in map_hint
    assert "QPSK" in next_step
