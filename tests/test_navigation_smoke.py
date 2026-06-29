"""Tests for the S035 navigation smoke helper."""

from tools.s035_navigation_smoke import run_smoke


def test_datoviz_fake_navigation_smoke_preserves_visual_upload_counts():
    result = run_smoke("datoviz-fake", steps=6, points=128)

    assert result["status"] == "passed"
    assert result["navigation_updates"] == 6
    assert result["visual_upload_calls_during_navigation"] == 0
    assert result["set_view2d_calls_during_navigation"] == 6
    assert result["set_domain_calls_during_navigation"] == 12


def test_matplotlib_navigation_smoke_records_frame_updates():
    result = run_smoke("matplotlib", steps=4, points=128)

    assert result["status"] == "passed"
    assert result["navigation_updates"] == 4
    assert result["frames_drawn"] == 4
    assert result["visual_upload_calls_during_navigation"] == 0
