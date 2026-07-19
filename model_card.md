# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  

Name: SongMap 1.0: 

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

New songs, all mapped to your tastes. SongMap is a program designed to generate song recommendations based on your preferences, whether it be by mood, genre, or energy. It weighs song attributes against a user's preferences and assigns a score to each song. Then the songs are ranked from highest to lowest score, highest meaning the song best matches the user. It assumes that the user wants a song that best matches their mood and energy (since this is more closely related to vibes), rather than just the genre. This is why energy and mood are given greater weights when deciding a song's score. Since this is just a simple system, this is just for classroom exploration. There is still a lot of bias involved because this system does not have a way to analyze user behavior (likes, playlists, most listened songs, etc.) and whether a user prioritizes genre, mood, and energy the most. Right now as the programmer, I am assuming the weights for each song attribute based on my personal preferences.


---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Each song has three attributes taken into account: genre, mood, and energy. The user profile contains a preferred genre, mood, and target energy level (as well as whether they like acoustics but that is not referenced in this system). For every song in the catalog, the recommender compares these features against the user's preferences.

Genre and mood are compared using exact string matches. If the values match, the song earns points. Energy is compared numerically by measuring how close the song's energy is to the user's preferred energy. Mood receives the highest weight (2.5), energy is weighted second (2.0), and genre is weighted third (1.0). After every song receives a score, the songs are sorted from highest to lowest, and the highest scoring songs are recommended first. Compared to the starter logic, I adjusted the weights to emphasize mood over genre because I wanted recommendations to prioritize a song's overall vibe rather than only its genre. Genre can also be very niche and specific and since this system will only give genre points for being an exact match, I felt that mood and energy can give songs that generally match a wide variety of genres.

---

## 4. Data  

Describe the dataset the model uses.  

The recommender uses a set of 15 songs stored in a CSV file. The dataset contains popular pop, rock, jazz, lofi, and ambient songs with moods such as happy, chill, and intense. Each song also includes numerical values like energy, tempo, valence, danceability, and acousticness, although only genre, mood, and energy are currently used for scoring.

I expanded the starter dataset by adding several popular songs to increase genre variety. However, the catalog is still small and does not represent every musical style or mood. Many combinations, such as chill pop or intense lofi, are missing, which limits the recommendations the system can produce. Also because the popular songs I added have very specific and uncommon genres and moods, they didn't seem to show up as often so the dataset doesn't include a wide variety of musical tastes.

---

## 5. Strengths  

Where does your system seem to work well  

The recommender performs well for users whose preferences closely match songs that exist in the dataset. For example, the aligned pop, rock, and lofi profiles consistently receive recommendations that fit both their desired mood and energy. In theses cases, it makes sense for the user's mood, energy and preferred genre to correlate and the recommender is able to match songs the best in these cases. The weighted scoring also does a good job distinguishing between users with opposite preferences, such as energetic pop fans versus relaxed lofi listeners.

The explanations generated for every recommendation also make the system easier to understand because users can see exactly which features contributed to each song's score.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

The system quietly favors users who prefer mid-energy songs because the dataset only has songs that span from 0.28-0.93. Also because genre is underweighted compared to mood and energy, a perfect genre match can lose to a totally different genre with a closer energy. This affects users with a niche genre interest. This system also favors people with common mood interests because the dataset mostly contains happy and chill songs. People who prefer these moods are most likely to get multiple songs that adhere to this while people who prefer moods will get at most, one song that matches their mood. This system also doesn't account for acoustics when this is something included in the user profile.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

### Logic experiment: Temporarily comment out the mood check to see how the rankings change

When I commented out the mood weight, I found that scores shrunk by a lot because mood was the highest weighing factor and this helped favor genre more for conflicting profiles. However, this also gave the aligned user profiles less accurate recommendations. For example, for the aligned pop profile, removing the mood check put an "energetic" song at #1 and the actual "happy" song (and perfect match) was at #2. This was because the energy matches the user's preference more.

### User profiles I tested

I ran eight profiles through the recommender in "main.py". Three were "aligned" (the genre, mood, and energy all point the same way, like a real fan), and five were edge cases where I combined conflicting preferences to see if the scoring could be tricked. All of them use the same rules: energy is always a number between 0.0 and 1.0 and every genre and mood is a string that has to be an exact match.

- pop (aligned) | pop, happy, 0.75
- rock (aligned) | rock, intense, 0.90
- lofi (aligned) | lofi, chill, 0.30
- edge_lofi_intense (edge) | lofi, intense, 1.0 (calm genre, but wants max hype)
- edge_ambient_hype (edge) | ambient, happy, 1.0 (calm genre, but wants max hype)
- edge_rock_mellow (edge) | rock, chill, 0.0 (loud genre, but wants total calm)
- edge_pop_chill (edge) | pop, chill, 0.85 (pop fan who wants a chill mood)
- edge_mood_vs_energy (edge) | jazz, intense, 0.1 (loud mood, but wants low energy)

### Comparing pairs of profiles (what changed and why)

-pop (aligned) vs lofi (aligned): These two are opposites. The pop fan
gets bright, high-energy pop songs (Sunrise City, Levitating) at the top,
while the lofi fan gets quiet, low-energy songs (Library Rain, Midnight
Coding). This makes sense because both users asked for opposite energy levels and opposite
moods, so the lists barely overlap. This is the system working correctly for users with completely different preferences.

-pop (aligned) vs rock (aligned): Both want high energy, but different
moods and genres. The pop fan's list has "happy" songs while the rock fan's
top pick is Storm Runner (the only rock/intense song), followed by Gym
Hero. Notice both lists share high-energy pop songs lower down because when
mood and genre don't match, similar energies is enough for a song to make it onto any recommendation list since it has such a high weight.

-lofi (aligned) vs edge_lofi_intense (edge): Same genre (lofi), but I flipped the
mood to "intense" and energy to max. The result flips almost completely: the
calm lofi user gets lofi songs at the top, but the "intense lofi" user gets
Gym Hero and Storm Runner first (loud pop/rock), and the real lofi songs drop
to the middle. This is because no lofi song is "intense," so the recommender looks at whatever is intense and the high energy request, which is the
loudest songs, rather than lofi songs. Asking for "intense lofi" limits a lofi request.

-edge_ambient_hype (edge) vs edge_rock_mellow (edge): One user asks a
calm genre (ambient) to be energetic while the other asks a loud genre
(rock) to be totally calm. In BOTH cases the genre the user wants barely
appears at the top. The "hype ambient" user gets happy pop songs; the "mellow
rock" user gets ambient and lofi songs. This is because the energy request holds more importance than the genre, so energy wins and the genre loses.

-edge_pop_chill (edge) vs pop (aligned): Same genre (pop), except I changed the mood
from "happy" to "chill" (and made the energy higher). The aligned pop fan gets pop
songs 1–3. But the "chill pop" fan gets ZERO pop in the top three — the top
three are all lofi/ambient chill songs, and the pop songs fall lower on the list.
This is because there are no chill pop songs in the database, so the mood gets favored and recommends the chill songs instead (which are not pop).

-edge_mood_vs_energy (edge) vs rock (aligned): Both ask for the "intense" mood, but
the edge case has a very low energy (0.1) and asks for jazz. The top two
results are still loud songs (Storm Runner, Gym Hero) even though the user
wanted low energy because the "intense" mood weighs more than the
energy similarity. The real jazz song only reaches #3. This shows mood can
overpower energy even when they conflict.

### What surprised me

The biggest surprise was how often the system ignores the genre the user actually asked for. In "edge_pop_chill", a person who said "pop" gets no pop songs in their top three. And in "edge_mood_vs_energy", someone asking for low energy jazz gets loud rock and pop first. I expected this because genre is weighed the lest while mood is the strongest (2.5). However, I feel this makes sense because genre can be very niche and a song can fit into multiple genres. However for our system, only one genre can be listed, which might not match the user's preference. This is why we look at mood because that is more general but can still point in the same direction as the genre. However, it is interesting how the the wanted genre gets overruled whenever the database has no song that fits all three preferences at once. This might also mean we just have to expand our database to include a greater variety of songs and preferences.

Another thing that surprised me was how often "Gym Hero" showed up in most lists. I think think this is mostly because it gets favored for users who liked loud/upbeat songs with high energy even if the genre or mood gets missed.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

In the future, I would include additional features such as tempo, valence, acousticness, artist similarity, and multiple genres per song. Allowing matches for similar genres or moods instead of the exact match would also improve recommendation quality. I also think this is how real recommendation systems work especially for more niche genres or moods.

I would also expand the song database significantly and introduce diversity into the recommendation algorithm, so the same songs do not appear repeatedly for different users. Finally, I would provide more detailed explanations that show how much each feature contributed to the final score, making the recommendations more transparent.

---

## 9. Personal Reflection  

A few sentences about your experience.  

This project helped me understand that recommendation systems are much more sorting and matching data. They depend on specific features, scoring rules, and the quality of the dataset. Even changing the weight by a little can change which songs are recommended.

One thing that was interesting was how easily bias appeared in such a simple system. Maybe it's because this is a simple model, but I wonder how biases would change for a more complicated system. The main bias I found was that because my dataset lacks certain genres and moods, some users consistently receive stronger recommendations than others. It made me realize why music apps put so much effort into collecting diverse data and analyzing user behavior, so they can accommodate each person's unique listening experience. This also made me realize that to reduce bias, the system must be tweaked to each user to give the most accurate recommendations.
