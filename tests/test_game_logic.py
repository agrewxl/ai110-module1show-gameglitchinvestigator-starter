from logic_utils import check_guess, message_for_outcome

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"

def test_secret_as_string_compares_numerically():
    # Regression test for the "impossible to win" bug: the secret used to
    # become a string, so 28 vs "27" compared as text. It must compare as
    # numbers — 28 > 27 is "Too High", and 27 == "27" is a "Win".
    assert check_guess(28, "27") == "Too High"
    assert check_guess(27, "27") == "Win"

def test_hint_message_matches_outcome():
    # Regression test for the backwards-hints bug: a "Too High" guess must
    # tell the player to go LOWER, and "Too Low" must say go HIGHER.
    assert "LOWER" in message_for_outcome("Too High")
    assert "HIGHER" in message_for_outcome("Too Low")
