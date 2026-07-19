# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

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

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
