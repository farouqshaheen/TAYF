import numpy as np

from simulation.scenarios import LinkParams
from visualization.interactive_heatmap import create_rich_heatmap
from visualization.interactive_oscilloscope import create_interactive_heartbeat


def test_interference_map_keeps_rssi_and_degrades_snr():
    params = LinkParams()
    rssi = create_rich_heatmap(params, suspect="الشبح", incident_t=1.0, metric="RSSI")
    snr = create_rich_heatmap(params, suspect="الشبح", incident_t=1.0, metric="SNR")

    rssi_values = np.asarray(rssi.data[0].z, dtype=float)
    snr_values = np.asarray(snr.data[0].z, dtype=float)

    assert np.isfinite(rssi_values).all()
    assert np.isfinite(snr_values).all()
    # Interference should affect the quality layer, not falsify received power.
    assert not np.allclose(rssi_values, snr_values)
    assert "SNR" in snr.layout.title.text


def test_heatmap_supports_2d_and_3d_views():
    params = LinkParams()
    flat = create_rich_heatmap(params, suspect="الظل", incident_t=0.6, view_mode="2D الخريطة الرادارية")
    surface = create_rich_heatmap(params, suspect="الظل", incident_t=0.6, view_mode="3D المجسم الطيفي")

    assert flat.data[0].type == "heatmap"
    assert surface.data[0].type == "surface"
    assert np.asarray(flat.data[0].z).shape == (56, 56)
    assert np.asarray(surface.data[0].z).shape == (56, 56)


def test_heartbeat_marks_selected_sample_and_incident_start():
    import pandas as pd

    frame = pd.DataFrame(
        {
            "timestamp_s": range(4),
            "phase": ["أساسي", "أساسي", "حادث", "حادث"],
            "rssi_dbm": [-50.0, -51.0, -60.0, -62.0],
            "snr_db": [30.0, 29.0, 18.0, 16.0],
        }
    )
    fig = create_interactive_heartbeat(frame, current_step=2)

    assert len(fig.data) == 4  # two traces plus one selected-point marker per trace
    assert any(shape.type == "rect" for shape in fig.layout.shapes)
    assert any(shape.type == "line" for shape in fig.layout.shapes)
