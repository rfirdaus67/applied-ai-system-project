# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This project implements a simple music recommender that matches songs to a user's preferences using a weighted scoring system. Each song is described by its genre, mood, and energy level, while a user profile stores the user's preferred values for those same features plus whether the user likes acoustics The recommender scores every song based on how closely it matches the user's preferences, ranks the songs from highest to lowest score, and returns the top recommendations along with explanations for why each song was selected.

---

## How The System Works

Explain your design in plain language.

You can include a simple diagram or bullet list if helpful.

In the real world, recomendations are made based on the user's listening activity and their behavior like skips, likes, etc. These systems also look at the songs being listened to and look into their mood, energy, and genre to make similar recomendations. 

Features Song class will have: genre, mood, and energy
Features UserProfile will have/store: favorite genre, preferred mood, and preferred energy and whether they like acoustics.

My Recommender computes a score by giving mood +2.5 points, energy +2.0 points, and genre +1.0 points, prioritizing mood. Since mood is a string and is the most depended on, if the moods aren't an exact match then no points are given. So even if a song has a similar mood which should be given more priority, they'll get another song most likely. Since genre and mood are strings, they are given a higher score if they are exact matches. Doing 1 - |song.energy - user.preferred_energy| for the energy score to see how close the energies are (closer to 1). Songs are recomended by having a score calculated for them then sorted from highest to lowest.
---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

The outputs/recommendations below are for the 5 different user profiles:

================================================
  Top 5 recommendations
  for happy / pop @ energy 0.8
================================================

1. Sunrise City — Neon Echo
   Score: 5.46
   Reasons:
     • mood matches (happy)
     • energy 0.82 vs preferred 0.80 (+1.96)
     • genre matches (pop)

2. Rooftop Lights — Indigo Parade
   Score: 4.42
   Reasons:
     • mood matches (happy)
     • energy 0.76 vs preferred 0.80 (+1.92)

3. Gym Hero — Max Pulse
   Score: 2.74
   Reasons:
     • energy 0.93 vs preferred 0.80 (+1.74)
     • genre matches (pop)

4. Levitating — Dua Lipa
   Score: 1.94
   Reasons:
     • energy 0.83 vs preferred 0.80 (+1.94)

5. Night Drive Loop — Neon Echo
   Score: 1.90
   Reasons:
     • energy 0.75 vs preferred 0.80 (+1.90)

```
================================================
  Top 5 recommendations
  for intense / jazz @ energy 0.1
================================================

1. Storm Runner — Voltline
   Score: 2.88
   Reasons:
     • mood matches (intense)
     • energy 0.91 vs preferred 0.10 (+0.38)

2. Gym Hero — Max Pulse
   Score: 2.84
   Reasons:
     • mood matches (intense)
     • energy 0.93 vs preferred 0.10 (+0.34)

3. Coffee Shop Stories — Slow Stereo
   Score: 2.46
   Reasons:
     • energy 0.37 vs preferred 0.10 (+1.46)
     • genre matches (jazz)

4. Spacewalk Thoughts — Orbit Bloom
   Score: 1.64
   Reasons:
     • energy 0.28 vs preferred 0.10 (+1.64)

5. Library Rain — Paper Lanterns
   Score: 1.50
   Reasons:
     • energy 0.35 vs preferred 0.10 (+1.50)
```
```
================================================
  Top 5 recommendations
  for chill / pop @ energy 0.85
================================================

1. Midnight Coding — LoRoom
   Score: 3.64
   Reasons:
     • mood matches (chill)
     • energy 0.42 vs preferred 0.85 (+1.14)

2. Library Rain — Paper Lanterns
   Score: 3.50
   Reasons:
     • mood matches (chill)
     • energy 0.35 vs preferred 0.85 (+1.00)

3. Spacewalk Thoughts — Orbit Bloom
   Score: 3.36
   Reasons:
     • mood matches (chill)
     • energy 0.28 vs preferred 0.85 (+0.86)

4. Levitating — Dua Lipa
   Score: 2.96
   Reasons:
     • energy 0.83 vs preferred 0.85 (+1.96)
     • genre matches (pop)

5. Sunrise City — Neon Echo
   Score: 2.94
   Reasons:
     • energy 0.82 vs preferred 0.85 (+1.94)
     • genre matches (pop)
```
```
================================================
  Top 5 recommendations
  for chill / rock @ energy 0.0
================================================

1. Spacewalk Thoughts — Orbit Bloom
   Score: 3.94
   Reasons:
     • mood matches (chill)
     • energy 0.28 vs preferred 0.00 (+1.44)

2. Library Rain — Paper Lanterns
   Score: 3.80
   Reasons:
     • mood matches (chill)
     • energy 0.35 vs preferred 0.00 (+1.30)

3. Midnight Coding — LoRoom
   Score: 3.66
   Reasons:
     • mood matches (chill)
     • energy 0.42 vs preferred 0.00 (+1.16)

4. Coffee Shop Stories — Slow Stereo
   Score: 1.26
   Reasons:
     • energy 0.37 vs preferred 0.00 (+1.26)

5. Focus Flow — LoRoom
   Score: 1.20
   Reasons:
     • energy 0.40 vs preferred 0.00 (+1.20)
```
```
================================================
  Top 5 recommendations
  for happy / ambient @ energy 1.0
================================================

1. Levitating — Dua Lipa
   Score: 4.16
   Reasons:
     • mood matches (happy)
     • energy 0.83 vs preferred 1.00 (+1.66)

2. Sunrise City — Neon Echo
   Score: 4.14
   Reasons:
     • mood matches (happy)
     • energy 0.82 vs preferred 1.00 (+1.64)

3. Rooftop Lights — Indigo Parade
   Score: 4.02
   Reasons:
     • mood matches (happy)
     • energy 0.76 vs preferred 1.00 (+1.52)

4. Gym Hero — Max Pulse
   Score: 1.86
   Reasons:
     • energy 0.93 vs preferred 1.00 (+1.86)

5. Storm Runner — Voltline
   Score: 1.82
   Reasons:
     • energy 0.91 vs preferred 1.00 (+1.82)
```
```
================================================
  Top 5 recommendations
  for intense / lofi @ energy 1.0
================================================

1. Gym Hero — Max Pulse
   Score: 4.36
   Reasons:
     • mood matches (intense)
     • energy 0.93 vs preferred 1.00 (+1.86)

2. Storm Runner — Voltline
   Score: 4.32
   Reasons:
     • mood matches (intense)
     • energy 0.91 vs preferred 1.00 (+1.82)

3. Midnight Coding — LoRoom
   Score: 1.84
   Reasons:
     • energy 0.42 vs preferred 1.00 (+0.84)
     • genre matches (lofi)

4. Focus Flow — LoRoom
   Score: 1.80
   Reasons:
     • energy 0.40 vs preferred 1.00 (+0.80)
     • genre matches (lofi)

5. Uptown Funk — Mark Ronson ft. Bruno Mars
   Score: 1.72
   Reasons:
     • energy 0.86 vs preferred 1.00 (+1.72)
```
**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. 

- Reduced the mood weight to zero by temporarily commenting out the mood check. This caused recommendations to rely much more on genre and energy. While genre appeared more often, recommendations felt less accurate because songs with the correct mood were no longer prioritized

- Tested several "aligned" user profiles where genre, mood, and energy naturally fit together (pop, rock, and lofi). These consistently produced recommendations that matched expectations.

- Created five edge case user profiles with conflicting preferences such as "intense lofi" or "happy ambient" at maximum energy. These experiments showed that when no song satisfies every preference, the recommender sacrifices genre to satisfy mood and energy because those attributes are weighed more

- Compared recommendation lists across different users to identify hidden biases. The same energetic songs frequently appeared near the top of many recommendation lists, showing that high weight features can overpower other preferences.

- Changed mood's weight from 2.5 to 2.0 and this helped the overpowering issue, giving songs with the same genre a chance to show up more often while still prioritizing mood and energy.

---

## Limitations and Risks

Summarize some limitations of your recommender.

- This recommender only truly works well with a small catalog of songs

- Unique combinations of genre, mood, and energy may not be handled correctly because the dataset prioritizes common combinations. When the exact combination is missing, the recommender falls back to whichever songs score highest on the most weighted features

- The system requires exact string matches for genre and mood. Similar genres (such as indie pop and pop) or related moods (happy and upbeat) are treated as completely different

- Since mood and energy receive higher weights than genre, users with niche genre preferences may receive recommendations from completely different genres if those songs better match the wanted mood or energy

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

Building this recommender helped me understand that recommendation systems heavily rely on the data they are fed (and trained with) and scoring rules. A simple weighted model can produce recommendations that feel reasonable, but the results depend heavily on the features being weighed and how much weight they are given. This depends on the creator of the program and what they prioritize rather than each user. I noticed that small changes to the weights noticeably changed the rankings, such as by lowering the weight of mood to 2.0 instead of 2.5

I also learned that bias can appear even without intending it. Since my dataset contains only a handful of genres and mostly happy or chill songs, some users naturally receive better recommendations than others. This gave me a better appreciation for why real recommendation systems require large, diverse datasets and constant evaluation to ensure they work fairly for many different users. Also because of my personal preferences, I gave more weight to mood and energy when maybe a user wants to find songs of the same genre instead. This also introduces a bias because I assume that by giving these attributes more weight, better recommendations can be given but that might not sit right with some users.



