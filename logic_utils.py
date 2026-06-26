def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    ranges = {
        "Easy": (1, 20),
        "Normal": (1, 100),
        "Hard": (1, 50),
    }
    return ranges.get(difficulty, (1, 100))


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None or str(raw).strip() == "":
        return False, None, "Enter a guess."

    try:
        # Accept "42" and "42.0", reject everything else.
        value = int(float(raw)) if "." in str(raw) else int(raw)
    except (ValueError, TypeError):
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return the outcome.

    Both values are coerced to int so the comparison is always numeric
    (never a lexicographic string compare).

    outcome: "Win", "Too High", or "Too Low"
    """
    # FIX: app.py used to turn the secret into a str on even turns, so an int
    # guess was compared lexicographically (28 < "27" as text). With my AI
    # assistant I traced the silent TypeError fallback and coerced both sides
    # to int here so the comparison is always numeric.
    guess = int(guess)
    secret = int(secret)

    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def message_for_outcome(outcome: str):
    """Return the player-facing hint that matches an outcome."""
    # FIX: the original hints were backwards ("Too High" showed "Go HIGHER!").
    # The AI suggested swapping the strings; I verified the mapping by hand and
    # added test_hint_message_matches_outcome to lock it in.
    return {
        "Win": "🎉 Correct!",
        "Too High": "📉 Go LOWER!",
        "Too Low": "📈 Go HIGHER!",
    }.get(outcome, "")


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        # Fewer attempts -> more points, with a floor of 10.
        return current_score + max(10, 100 - 10 * attempt_number)

    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
