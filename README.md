# 🎵 AI DJ + Music Recommender

---

## Original Project (Modules 1-3): 🎵 Music Recommender Simulation

Goals:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong

This project implements a simple music recommender that matches songs to a user's preferences using a weighted scoring system. Each song is described by its genre, mood, and energy level, while a user profile stores the user's preferred values for those same features. The recommender scores every song based on how closely it matches the user's preferences, ranks the songs from highest to lowest score, and returns the top recommendations along with explanations for why each song was selected.

---

## Title and Summary

Title: AI Music DJ

Summary: This system takes in the user's preferences, turns the songs into vectors, and scores them with cosine similarity so it can recommend the songs that best fit the user. The Gemini agent then explains why each song was picked. This project matters because the original system was much more strict. It could only take one mood and genre and if they weren't an exact match, no points were given. Using vectors and cosine similarity, a song like "alt-rock" still earns partial credit against "rock" instead of getting nothing, which is closer to how real recommendation systems work. My first version of this let the Gemini agent read the whole CSV and judge everything itself, but that overloaded the agent and gave me different results every time I ran the same preferences. Now the scoring happens in Python and the agent only gets the 5 winning songs in chunks, so the recommendations are consistent and the agent has a much smaller job.

---

## Architecture Overview

- User inputs their preferred genre(s), mood(s), and energy level and ranks which attributes they want prioritized more (1 = most prioritized, 3 = least prioritized) on streamlit interface

- Preferences and rankings are fed into ranking.py, where weights are assigned to each attribute based on ranking (Ex: #1 ranking = 6.0)

- ranking.py also loads spotify_songs.csv and uses CountVectorizer to turn every song's genre and mood into a vector, then compares them to the user's genre and mood with cosine similarity. Energy is compared with distance (1 - the difference), since it's already a number

- The three similarity scores get multiplied by the user's weights and added together, then divided by the total weight so every song ends up with a final score from 0.00 to 1.00. The 5 highest scoring songs are the recommendations

- scoring.py takes just those 5 songs and turns them back into CSV rows, then sends them to the Gemini agent in chunks of 2 rows at a time instead of uploading the entire dataset

- Gemini only writes the explanation for each of those 5 songs. It isn't allowed to reorder them, add songs, or change the scores. Streamlit shows the score table first, then the explanations, and the user can regenerate if wanted

---

## Setup Instructions

1. Create a virtual environment:

```bash
pip install python-dotenv
```
OR

```bash
python -m venv .venv
source .venv/bin/activate      # Mac or Linux
.venv\Scripts\activate         # Windows
```

2. Install dependencies


```bash
pip install -r requirements.txt
```
3. Create your Gemini API key on https://ai.google.dev/gemini-api/docs/api-key


4. Paste your API Key into .env.example & rename file to .env


5. Change model if needed in gemini.py (Recommended model: gemini-3.6-flash)


6. Run the program:


```bash
streamlit run app.py (from src)
```
---
## Sample Interactions/Outputs


Can also run main.py to see user profile and preference examples and their outputs. It prints the cosine similarity ranking first, then the chunks that actually get sent to Gemini, then Gemini's explanations:


```
==============================================================================
Example 1 — Energy-first workout playlist
------------------------------------------------------------------------------
  Genre:      pop
  Mood:       Energetic
  Energy:     0.95
  Priority:   Energy > Genre > Mood  (1st = most weight)
  Weights:    {'energy': 6.0, 'genre': 3.0, 'mood': 1.0}
------------------------------------------------------------------------------
Cosine similarity ranking:

       artists      track_name track_genre      mood  energy  final_score
       YOASOBI           夜に駆ける       j-pop Energetic   0.874     0.954400
Gajendra Verma       Mann Mera    pop-film Energetic   0.765     0.801132
    The Weeknd Blinding Lights         pop     Happy   0.730     0.768000
    Nogizaka46           月の大きさ      j-idol Energetic   0.941     0.694600
       Blondie  Heart Of Glass   power-pop     Happy   0.725     0.677132
```

Those 5 songs are all that gets sent to Gemini, as CSV chunks of 2 rows each:

```
rank,artists,track_name,energy,track_genre,mood,score
1,YOASOBI,夜に駆ける,0.874,j-pop,Energetic,0.954
2,Gajendra Verma,Mann Mera,0.765,pop-film,Energetic,0.801
3,The Weeknd,Blinding Lights,0.730,pop,Happy,0.768
4,Nogizaka46,月の大きさ,0.941,j-idol,Energetic,0.695
5,Blondie,Heart Of Glass,0.725,power-pop,Happy,0.677
```

Gemini then returns one explanation per song and app.py renders each one as the title, the score, and the reason on their own lines:

```
**1. 夜に駆ける - YOASOBI**

**Score:** 0.954

[Gemini's explanation of why this song scored highest]
```

```
==============================================================================
Example 2 — Mood-first mellow evening
------------------------------------------------------------------------------
  Genre:      acoustic
  Mood:       Chill
  Energy:     0.3
  Priority:   Mood > Energy > Genre  (1st = most weight)
  Weights:    {'mood': 6.0, 'energy': 3.0, 'genre': 1.0}
------------------------------------------------------------------------------
Cosine similarity ranking:

             artists                  track_name track_genre  mood  energy  final_score
         Gen Hoshino                      Comedy    acoustic Chill   0.461       0.9517
     Bombay Jayashri                   Zara Zara   classical Chill   0.268       0.8904
        George Jones He Stopped Loving Her Today  honky-tonk Chill   0.232       0.8796
         Hans Zimmer             Cornfield Chase      german Chill   0.226       0.8778
Cigarettes After Sex                          K.     ambient Chill   0.400       0.8700
```

You can see the ranking react to what the user prioritized. In Example 1 energy is #1, so every recommendation sits near 0.95 energy even when the genre isn't exactly pop. In Example 2 mood is #1, so all 5 songs are Chill and the system gives up on the acoustic genre to get there. Running either example again gives back the exact same 5 songs in the same order, which my old version could not do.

---

## Design Decisions

The problem I was trying to solve is that the original system was too strict. Genre and mood only counted if they were an exact match, so anything close got zero points and the recommendations were repetitive. My first fix was to hand the whole thing to the Gemini agent. I uploaded the entire CSV and let it decide which songs were similar and rank them itself. That did solve the strictness, but it created bigger problems. Uploading the whole dataset overloaded the agent, which is why I had to cut my dataset down to about 100 songs in the first place, and even then the same exact preferences gave me a different top 5 every time I ran it. I also had no way to prove the agent was applying my weights instead of its own opinion.

So I changed who does the judging. Now ranking.py uses CountVectorizer to turn each song's genre and mood into a vector and compares them to the user's input with cosine similarity. That gives me the "similar but not exact" behavior I wanted from the agent, except I can actually see the number. "alt-rock" scores 0.707 against "rock" because they share one word out of two, and "classical" scores 0.000. Energy is just 1 minus the distance between the song's energy and what the user asked for. Then each of those three scores gets multiplied by the weight for that attribute and divided by the total weight so the final score lands between 0.00 and 1.00.

The weights themselves are the one thing I kept exactly the same. Whatever the user ranks #1 gets 6.0, #2 gets 3.0, and #3 gets 1.0. In my original system they were 2.5, 2.0 and 1.0 but the #1 ranking wasn't dominating enough to actually be visible in the recommendations. I kept 6.0/3.0/1.0 because 6 is bigger than 3 and 1 put together, so the user's top priority always wins and the other two only break ties.

The other big change was what the agent receives. Instead of the whole CSV, it now only gets the 5 songs that already won, sent as CSV rows in chunks of 2. That's a few hundred tokens instead of the entire dataset, and since the agent never sees the songs that lost, it can't quietly swap one in. I also told it in the prompt that it cannot reorder, add, drop, or recompute anything, and I made it return JSON with just the explanation sentences so the title and score in the output come from my DataFrame and not from the model.

The tradeoff is that I gave up the agent's actual music knowledge. CountVectorizer only compares words, so it doesn't know that "j-idol" and "pop" are related the way Gemini did. It only matched those two in Example 1 because energy and the shared word carried the score. There are also some quirks I had to accept, like "j-rock" scoring a perfect 1.000 against "rock" because CountVectorizer ignores single letters, so the "j" gets dropped. I decided consistent and explainable was worth more than smart but unpredictable, since I can defend a number but I couldn't defend the agent's opinion. The user still has the option to regenerate if they don't like what they get, but there is no feedback loop or history, so the system doesn't know why they regenerated and doesn't learn from it.

---

## Testing Summary

I wrote tests in test_ranking.py that check the ranking-to-weight logic across all the different ways a user can rank the attributes, plus edge cases like only ranking one or none of them. These showed that whatever the user ranks #1 always gets the highest weight and that it makes it into the Gemini prompt correctly. I also made sure the tests confirmed key info was always included in the prompt. What worked was pulling the ranking logic out along with the user's preferences so I could test it without launching Streamlit.

The biggest change to my testing is that now I can actually test the recommendations themselves, not just the prompt. Before, my pytests passed but the recommendations still felt off, because my tests could only prove the weights and prompt info were correct, not that the AI applied them. That was the real bug and pytest couldn't catch it. Now that the scoring happens in Python, I can test it directly. I have tests that check an exact genre match beats an unrelated one, that "alt-rock" lands in between an exact match and something with no words in common, that the energy score really is 1 minus the distance, and that flipping which attribute is ranked #1 changes which song wins. I also have a test that runs the same preferences twice and asserts it gets the same 5 songs back, which is the thing my old version could never pass.

test_scoring.py covers the part that goes to the agent and comes back. It checks that the chunks split where they should, that a song title with a comma in it doesn't break the CSV rows, that the song ID never leaks into the prompt, and that the title/score/explanation layout is built correctly even if Gemini returns fewer explanations than songs. Since the score printed to the user is pulled from my DataFrame, there's a test proving that even if the model says the wrong number in its text, the score shown is still mine.

What I still can't test is the quality of the explanation sentences themselves. That part is still the agent and still needs a human to read it, but now the worst case is a badly worded explanation instead of a wrong recommendation.

---

## Reliability & Evaluation (Testing cont.)

Run the automated tests with:

```bash
pytest
```

All 39 out of 39 tests passed (24 in test_ranking.py, 15 in test_scoring.py). The suite verifies that ranked attributes always get their matching weight (rank #1 → 6.0, #2 → 3.0, #3 → 1.0), that it defaults to 0.33 for partial/empty rankings, and that the required info always makes it into the prompt: the user's genre/mood/energy and their assigned weight are guaranteed to appear and the top-ranked feature is named as the dominant one. It also verifies the cosine similarity scoring itself, that every final score lands between 0.00 and 1.00, and that the same preferences give back the same 5 songs.

Since the scores are now on a 0.00 to 1.00 scale, they read differently than they did before. Using the example preferences in main.py (Energy-first pop/Energetic/0.95, and Mood-first acoustic/Chill/0.3), the #1 recommendation scores around 0.95 when the dataset actually contains a good match. The next few usually fall between 0.95 and 0.65, and the drop-off gets steeper the more niche the input is, because a rare genre means fewer songs share any words with it. The scores are also only comparable inside one search, since a low top score usually means the dataset just doesn't have what the user asked for.

Human Evaluation Table:

| Test Input | Evaluation Criteria | Result |
| --- | --- | --- |
| No input for genre and mood | Handles gracefully and still gives recommendations based on energy | Pass - genre and mood score 0.00 for every song so energy decides the ranking on its own |
| AI model is busy/error generating response | Displays the error message from Gemini | Fail - no explanations, though the songs and scores are already decided before the agent is ever called |
| No rankings selected | Alerts the user they need to rank the attributes | Pass - doesn't give output without this critical info |
| Genre = Kpop (#1) & Mood: Feel-good (#2) & Energy: 0.25 (#3) | Top 3 recommendations are of same/similar genre | Pass - the most weighted attribute (genre) dominates the recommendations and matches user's ranking |
| Genre = Kpop, Indian (#1) & Mood: = Feel-good, Energetic (#3) & Energy = 0.55 (#2) | All recommendations have similar genres and energy | Pass - Shows multiple genres and moods work for flexibility |
| Same preferences submitted twice in a row | Returns the identical top 5 in the identical order | Pass - this failed on my old version, where the agent reshuffled the list every run |
| Song title containing a comma | The CSV chunk sent to the agent doesn't get split into the wrong columns | Pass - the row is quoted so it still parses into 7 fields |

---

## Reflection

This project taught me that there is always some uncertainty involved with AI. No matter how good or specifically you prompt it, you can't always guarantee it will work the way you want. Handing the logic to an agent definitely saved me time up front and made the system easier to walk through, but I couldn't be sure it would solve the problem the same way twice, or solve it the way I would have.

What changed my mind was realizing I was using the agent for two completely different jobs at once. Deciding which songs win is math, and math should be the same every time. Explaining why a song won is writing, and that's the part an agent is actually good at. When I gave it both, the part it was good at came with a part I couldn't trust or test. Splitting them meant the scoring became something I could prove with pytest, and the agent got a job small enough that it can't really get it wrong.

The other lesson was about how much you feed a model. I assumed giving Gemini the whole CSV would make it smarter, but it just overloaded it and forced me to shrink my dataset to 100 songs. Sending 5 rows in chunks instead means the dataset could grow to thousands of songs now, because Python does the searching and the agent only ever sees what already won. So the thing that made the system more reliable also made it able to scale, which I did not expect going in.