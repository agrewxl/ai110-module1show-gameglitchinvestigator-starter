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

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
