# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The first time I ran the game it *looked* fine — a title, a difficulty selector, a guess box, and a "Developer Debug Info" panel that even showed me the secret number. But it was unplayable. The hints lied, the secret number seemed to change between guesses, and there was no number I could enter that would ever win.

Concrete bugs I noticed:

1. **No winnable number / secret "changes its mind."** The debug panel showed the secret as 27, but when I guessed 27 the game said "Go HIGHER!", and when I guessed 28 it said "Go LOWER!". There was literally no value that registered as correct. Looking at the code, on every *even* attempt the secret is converted to a string (`str(st.session_state.secret)`), so an integer guess is compared against a string. That throws a `TypeError` which gets caught and silently falls back to comparing the numbers as *text* (lexicographic order), so the hints stop making numeric sense and the game becomes impossible to win.

2. **The hints are backwards.** In `check_guess`, when the guess is greater than the secret (i.e. "Too High"), the message returned is "📈 Go HIGHER!" instead of "Go LOWER!". The outcome label and the message it shows the player directly contradict each other, so even on a normal turn the hint points you the wrong way.

3. **"New Game" doesn't actually restart the game.** Clicking "New Game 🔁" resets `attempts` but never resets `status`, `score`, or `history`. So after you lose, the status stays `"lost"` and the page immediately calls `st.stop()` — you're stuck on "Game over" and can't start over. It also rolls a new secret with `randint(1, 100)`, ignoring the difficulty range (e.g. on Easy the range is 1–20, but the answer could be 87 and unguessable).

4. **Wrong range text and an off-by-one attempt counter.** The prompt always says "Guess a number between 1 and 100" even on Easy (range 1–20) or Hard (range 1–50). Attempts also start at `1` instead of `0`, so "Attempts left" is one lower than it should be from the very first turn.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Guess `27` when Debug panel shows Secret = 27 | "🎉 Correct!" — a win | "📈 Go HIGHER!"; then guessing `28` shows "📉 Go LOWER!" — no value ever wins | none (TypeError silently caught, falls back to string compare) |
| Guess `60` when secret = 50 (odd attempt) | Outcome "Too High" → hint should say go LOWER | Outcome is "Too High" but message shown is "📈 Go HIGHER!" (message inverted) | none |
| Guess `9` on the 2nd (even) attempt when secret = 80 | "Too Low" → go HIGHER (9 < 80) | String compare: `"9" > "80"` is True, so it says "Too High" / "Go HIGHER!" | none (int-vs-str TypeError caught internally) |
| Lose a game, then click "New Game 🔁" | Fresh, playable game: score 0, attempts/history reset | Still shows "Game over." and locks the board (`st.stop()`); score and history not cleared | none |
| Set difficulty to **Easy** (range 1–20) and read the prompt | "Guess a number between 1 and 20" | Always reads "between 1 and 100"; New Game can even pick a secret outside the Easy range | none |

---

## 2. How did you use AI as a teammate?

I used an AI coding assistant in the editor (chat + agent edits) as my debugging partner. I worked one bug per chat so it stayed focused, attached `app.py` and `logic_utils.py` together so it could see how the UI and logic related, and reviewed every diff before accepting it.

**A correct suggestion.** When I asked why no number ever won, the AI pointed at the lines in `app.py` that did `secret = str(st.session_state.secret)` on even attempts and explained that comparing an `int` guess to a `str` secret raised a `TypeError` that the `check_guess` fallback silently swallowed, leaving a lexicographic string comparison. Its fix was to stop stringifying the secret and coerce both values to `int` inside `check_guess`. I verified this two ways: I wrote `test_secret_as_string_compares_numerically` (asserting `check_guess(28, "27") == "Too High"` and `check_guess(27, "27") == "Win"`) and it passed, and I played the live game — the secret shown in the debug panel was finally winnable.

**An incorrect / misleading suggestion.** While fixing the backwards hints, the assistant first suggested I just swap the *outcome labels* (return "Too Low" when `guess > secret`). That would have made the hint text read correctly but broken the meaning of the outcome — and it would have failed the existing `test_guess_too_high` test (which expects `check_guess(60, 50) == "Too High"`). I caught it by re-reading the test file, then chose the correct fix instead: keep the outcomes accurate and only correct the player-facing message in `message_for_outcome` ("Too High" → "Go LOWER!"). Running pytest confirmed the original tests still passed, proving the AI's first idea was the wrong layer to change.

---

## 3. Debugging and testing your fixes

I decided a bug was really fixed only when it was locked down by a test *and* confirmed in the live app — not just because the code "looked right." For each fix I added a regression test that would fail on the old behavior, then ran `pytest tests/ -v`.

The most useful test was `test_secret_as_string_compares_numerically`. Passing it proved the impossible-win bug was gone, because the test reproduces the exact broken case (an int guess vs a string secret) and asserts a numeric result. I also added `test_hint_message_matches_outcome` to guarantee "Too High" tells the player to go LOWER. The full suite went from 3 to 5 tests, all passing:

```
tests/test_game_logic.py::test_winning_guess PASSED
tests/test_game_logic.py::test_guess_too_high PASSED
tests/test_game_logic.py::test_guess_too_low PASSED
tests/test_game_logic.py::test_secret_as_string_compares_numerically PASSED
tests/test_game_logic.py::test_hint_message_matches_outcome PASSED
========================= 5 passed in 0.01s =========================
```

AI helped me design the tests by suggesting the specific input/expected pairs that would target each bug (e.g. "test 28 against a string '27'"), but I decided *what* the correct behavior should be and reviewed each assertion before running it. Finally I ran `streamlit run app.py` and played a full round — winning, losing, and clicking "New Game" — to confirm the fixes hold in the real UI, not just in the test harness.

---

## 4. What did you learn about Streamlit and state?

The biggest thing I learned is that Streamlit re-runs the *entire* `app.py` from top to bottom every single time you interact with the page — click a button, type in a box, change the dropdown. I'd explain it to a friend like this: imagine your whole script is re-read out loud from scratch on every click, so any normal variable you set is forgotten the instant the next click happens. That's why the secret number "had commitment issues" — if it weren't stored specially, it would be re-rolled on every rerun. `st.session_state` is the fix: it's a little dictionary that *survives* between reruns, like a backpack you carry across each restart. So the secret, score, attempts, and status all have to live in `st.session_state` (and only be initialized if they aren't already there) so they persist while everything else gets rebuilt. Understanding this also explained the New Game bug: resetting one key in session state isn't enough — you have to reset every key that carries state, or stale values leak into the "new" game.

---

## 5. Looking ahead: your developer habits

The habit I most want to keep is **writing a failing regression test before I trust a fix**. Reproducing the bug as a test first (e.g. an int guess vs a string secret) meant I knew exactly when it was truly fixed, and the test stays around to stop the bug from coming back. I also want to keep committing in small, labeled steps — one commit for logging the bugs, one for the fixes, one for docs — because the history tells the story of my reasoning.

One thing I'd do differently is **give the AI more context up front and trust its first answer less**. Early on I accepted suggestions a bit too quickly; I got better results once I attached both `app.py` and `logic_utils.py` together and explicitly told it about the existing tests, so it stopped proposing fixes that would break them.

This project changed how I see AI-generated code: it's a fast, confident *first draft*, not a finished product. The starter code literally claimed to be "production-ready" and was unplayable — so now I treat AI output as something I have to read, question, and verify with tests rather than something I can paste in and ship.
