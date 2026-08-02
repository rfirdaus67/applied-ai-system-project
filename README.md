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

Summary: This system utilizes the Gemini API agent to take in user preferences and read a dataset of songs to recommend songs that best fit the user. This project matters because without using an agent, the original system was much more strict. It could only take one mood and genre and if they weren't an exact match, no points were given. By prompting the Gemini agent, we can now account for similarity instead of exact matches, which more closely resembles real recommendation systems. All without building more complex backend code.

---

## Architecture Overview

- User inputs their preferred genre(s), mood(s), and energy level and ranks which attributes they want prioritized more (1 = most prioritized, 3 = least prioritized) on streamlit interface

- Preferences and rankings are fed into ranking.py, where weights are assigned to each attribute based on ranking (Ex: #1 ranking = 6.0)

- ranking.py returns a specific prompt containing the user info (RAG payload) that is fed into Gemini agent

- Gemini returns top 5 recommended songs and why on streamlit interface, where the user can review the results and regenerate if wanted

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


Can also run main.py to see user profile and preference examples and their outputs:


```
==============================================================================
Example 1 — Energy-first workout playlist
------------------------------------------------------------------------------
 Genre:      pop
 Mood:       Energetic
 Energy:     0.95
 Priority:   Energy > Genre > Mood  (1st = most weight)
 Weights:    {'genre': 3.0, 'mood': 1.0, 'energy': 6.0}
------------------------------------------------------------------------------
AI recommendations:
Here are the top 5 song recommendations based on your preferences: genre=pop, mood=Energetic, energy=0.95, with energy being the most important factor.

---

**1. Nogizaka46 - 月の大きさ**
*   **Score:** 9.946
*   **Explanation:** This song is an excellent match, scoring high due to its very close energy level to your preference and perfectly matching your desired mood. Its J-idol genre is also highly similar to pop.
*   **Energy:** 0.941 (Your preferred energy: 0.95)

**2. Mr. C - Cha Cha Slide**
*   **Score:** 9.73
*   **Explanation:** A strong contender, this track's energy is very close to your preference, and its mood is an exact match for energetic. The 'kids' genre often features pop-like structures, making it a good fit.
*   **Energy:** 0.905 (Your preferred energy: 0.95

**3. Pinkfong - Baby Shark**
*   **Score:** 9.616
*   **Explanation:** This song offers a great energy level that is quite close to your preference, alongside an exact match for the energetic mood. Its 'children' genre is considered similar to pop for its catchy and simple structure.
*   **Energy:** 0.886 (Your preferred energy: 0.95)

**4. YOASOBI - 夜に駆ける**
*   **Score:** 9.544
*   **Explanation:** This J-pop track aligns well with your preferences, featuring an energetic mood and a good energy level that is close to your ideal. Its genre is also a direct match for a pop-like sound.
*   **Energy:** 0.874 (Your preferred energy: 0.95)

**5. Kenshi Yonezu - IRIS OUT**
*   **Score:** 9.52
*   **Explanation:** With an energetic mood and a very close energy level, this Anime genre track is a great choice. Anime music frequently incorporates pop elements, making it a strong stylistic match.
*   **Energy:** 0.87 (Your preferred energy: 0.95)
```

```
==============================================================================
Example 2 — Mood-first mellow evening
------------------------------------------------------------------------------
 Genre:      acoustic
 Mood:       Chill
 Energy:     0.3
 Priority:   Mood > Energy > Genre  (1st = most weight)
 Weights:    {'genre': 1.0, 'mood': 6.0, 'energy': 3.0}
------------------------------------------------------------------------------
AI recommendations:

Here are the top 5 songs that best match your preferences:

1.  **Zara Zara** by Bombay Jayashri
   *   **Score:** 9.904
   *   **Explanation:** This song is an excellent match because its mood is 'Chill', perfectly aligning with your preference. Its genre, 'classical', is also very similar to 'acoustic'. The energy of 0.268 is very close to your preferred 0.3.
   *   **Energy:** 0.268 (User's preferred energy: 0.3)

2.  **double take** by dhruv
   *   **Score:** 9.589
   *   **Explanation:** This song is a great match as its mood is 'Chill', which perfectly matches your preference. Its genre 'chill' is also similar to 'acoustic', and its energy of 0.437 is fairly close to your preferred 0.3.
   *   **Energy:** 0.437 (User's preferred energy: 0.3)

3.  **Comedy** by Gen Hoshino
   *   **Score:** 9.517
   *   **Explanation:** This song is a strong match because its genre is 'acoustic' and its mood is 'Chill', both exact matches to your preferences. The energy of 0.461 is also quite close to your preferred 0.3.
   *   **Energy:** 0.461 (User's preferred energy: 0.3)

4.  **i miss you** by Ichika Nito
   *   **Score:** 9.433
   *   **Explanation:** This song is a great fit with a 'Chill' mood, perfectly matching your preference. Its 'guitar' genre is similar to 'acoustic', and its energy of 0.489 is reasonably close to your preferred 0.3.
   *   **Energy:** 0.489 (User's preferred energy: 0.3)

5.  **Until I Found You (with Em Beihold) - Em Beihold Version** by Stephen Sanchez;Em Beihold
   *   **Score:** 9.250
   *   **Explanation:** This song aligns well with your preferences, featuring a 'Mellow' mood which is similar to 'Chill'. Its 'singer-songwriter' genre is also similar to 'acoustic'. The energy of 0.55 is a bit further from your preferred 0.3 but still contributes positively.
   *   **Energy:** 0.550 (User's preferred energy: 0.3)
```
---

## Design Decisions

I built the model this way because instead of writing up a complex backend in python that can change the weights of each attribute and isn't so strict, I let AI handle it. The weight assigning is not the difficult part, but rather the judging of similar genres/moods when they aren't exact matches. This is why expanding the dataset to have varying genres and songs was also important. The benefit of having the user choose what they want to prioritize the most if they have a contrasting mood and genre is they can still get recommendations catered to them. With this architecture, the system isn't just picking the same songs over and over again because there is no room for "similarity". Instead of being a difficult edge case like with our original system when the weights were strictly written for each attribute, this gives the user more flexibility and control over their recommendations.

However, this also leads to tradeoffs. To make the user's ranking of attributes become more apparent in the recommendations, I changed the weights to 6.0, 3.0, and 1.0. In my original system, they were 2.5, 2.0 and 1.0 but I noticed that what the user's #1 ranking wasn't dominating enough so it wasn't apparent in the recommendations. As far as testing goes, I can send the AI the weights each attribute is supposed to have but I have no way to determine that the AI is actually applying the weights. AI's judgement might get in the way of how different factors in songs should really be weighed, hence why the same prompt/preferences can lead to similar yet different outputs. Since genre and mood are very vague and can be unique, I let the AI completely judge whether genres and moods are "similar." For example, indie-pop might seem totally different from just kpop to us but because pop is a word in both, AI might think of them as similar. Also the user has the option to regenerate if they don't like the songs they get, but there is not feedback loop or history. The AI doesn't know why the user is regenerating and the AI doesn't check or learn from its recommendations.

---

## Testing Summary

I wrote  tests in test_ranking.py that check the ranking-to-weight logic across all the different ways a user can rank the attributes, plus edge cases like only ranking one or none of them. These showed that whatever the user ranks #1 always gets the highest weight and that it makes it into the Gemini prompt correctly. I also made sure the tests confirmed key info was always included in the prompt. What worked was pulling the ranking logic out along with the user's preferences so I could test it without launching Streamlit. What didn't work at first was that the pytests passed but the recommendations still felt off, and that's when I realized that my tests can only prove the weights and prompt info are correct, not that the AI actually applied them. I don't know how much the AI is using its own judgement and if this contradicts or skews the recommendations a certain way (from the AI's bias perhaps) or deviates from the weights/ranking system. The real bug is not something that can be shown through manual testing like pytest. Instead, the recommendations definitely need to be analyzed by a human when the same preferences occur and to see if the most weighted things are easily seen in the recommendations.

---

## Reliability & Evaluation (Testing cont.)

Run the automated tests in test_ranking.py with:

```bash
pytest tests/test_ranking.py
```

All 16 out of 16 ranking tests passed. The suite verifies that however ranked attributes always get their matching weight (rank #1 → 6.0, #2 → 3.0, #3 → 1.0), it defaults to 0.33 for partial/empty rankings, and that the required info always makes it into the prompt: the user's genre/mood/energy and their assigned weight are guaranteed to appear and the top-ranked feature is the most dominant. Using the example preferences cases like the ones in main.py (e.g. Energy-first pop/Energetic/0.95, and Mood-first acoustic/Chill/0.3), the AI's #1 recommendation score is very close to 9. The next 2 scores usually fall between 9-6 and the last 2 scores can be anywhere from 9-2 depending on the user input (if its niche or reflected well in the dataset and a "happy" case or edge case).

Human Evaluation Table:

| Test Input | Evaluation Criteria | Result|
| --- | --- | --- |
| No input for genre and mood | Handles gracefully and still gives recommendations based on energy| Pass - notes that the user did not give a genre and mood |
| AI model is busy/error generating response | Displays the error message from Gemini | Fail - doesn't give any recommendations |
| No rankings selected | Alerts the user they need to rank the attributes | Pass - doesn't give output without this critical info |
| Genre: Kpop (#1), Mood: Feel-good (#2), Energy: 0.25 (#3) |  | Top 3 recommendations are of same/similar genre, last 2 look at other attributes when genre can't be looked at | Pass - the most weighted attribute (genre) dominates the recommendations and matches user's ranking |
| Genre: Kpop, Indian (#1), Mood: Feel-good, Energetic (#3), Energy: 0.55 (#2) |  | All recommendations are of the said genres and the top 3 have similar energy levels. Both genres and moods input are reflected | Pass - Multiple genres and moods work for flexability  |

---

## Reflection

This project taught me that there is always some uncertainty involved with AI. No matter how good or specifically you prompt it, you can't always guarantee it will work the way you want. When it comes to problem-solving, integrating AI into your work to do the logic definitely saves time and makes for an "easier to walk-through" system. However, you can't be sure that it will solve the problem or task you're giving it the same every time or problem solving the way you would.