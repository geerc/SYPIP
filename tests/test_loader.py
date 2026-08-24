from sleeper_rankings.loader import completed_week, team_name


def test_completed_week_defaults_to_zero():
    assert completed_week({"settings": {}}) == 0


def test_team_name_falls_back_to_display_name():
    assert team_name({"display_name": "Chris", "metadata": {}}, 1) == "Chris"

