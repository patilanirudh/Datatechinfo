from app.services.congestion_calculator import compute_congestion


def test_free_flow_when_ratio_low():
    result = compute_congestion(current_travel_time_s=100, free_flow_travel_time_s=95, road_closure=False)
    assert result.severity == "free_flow"


def test_moderate_congestion():
    result = compute_congestion(current_travel_time_s=130, free_flow_travel_time_s=100, road_closure=False)
    assert result.severity == "moderate"


def test_high_congestion():
    result = compute_congestion(current_travel_time_s=180, free_flow_travel_time_s=100, road_closure=False)
    assert result.severity == "high"


def test_severe_congestion():
    result = compute_congestion(current_travel_time_s=300, free_flow_travel_time_s=100, road_closure=False)
    assert result.severity == "severe"
    assert result.congestion_ratio == 3.0


def test_road_closure_overrides_ratio():
    result = compute_congestion(current_travel_time_s=100, free_flow_travel_time_s=100, road_closure=True)
    assert result.severity == "closed"


def test_zero_free_flow_time_does_not_crash():
    result = compute_congestion(current_travel_time_s=50, free_flow_travel_time_s=0, road_closure=False)
    assert result.severity == "free_flow"
