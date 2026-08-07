# 🎧 Model Card: Music Recommender Simulation

---

## 1. Model Name 


Give your model a short, descriptive name. 


Name: AI Music DJ

---

## 2. Intended Use 

Describe what your recommender is designed to do and who it is for.

The AI Music DJ is a program designed to generate song recommendations based on your preferences, whether it be by mood, genre, or energy. It lets the user input their preferred genre(s), mood(s), and energy level and rank which one is most important to them. Those preferences get turned into vectors and compared to every song in the dataset with cosine similarity, and each song gets a score out of 1.00. The songs are ranked from highest to lowest score, highest meaning the song best matches the user, and the top 5 are the recommendations. The Gemini agent comes in after that, and its only job is to explain why each of those 5 songs scored the way it did.

---

## 3. How the Model Works 

Explain your scoring approach in simple language. 

Each song has three attributes taken into account: genre, mood, and energy. The user is able to input a preferred genre, mood, and energy level and rank them for their recommendations. For every song in the catalog, the recommender compares these features against the user's preferences.

Genre and mood are compared using vectors. CountVectorizer turns every song's genre into a vector of the words it contains, and does the same for mood, and then cosine similarity measures how close the user's input is to each song. This is what lets a near match still count for something instead of being thrown out. "rock" against "rock" scores 1.000, "alt-rock" scores 0.707 because it shares one word out of two, and "classical" scores 0.000 because it has nothing in common. Energy is compared numerically by measuring how close the song's energy is to the user's preferred energy, using 1 minus the difference between them.

Whichever attribute is ranked #1 has the highest weight (6.0), #2 ranked is weighted second (3.0), and #3 ranked is weighted third (1.0). Each of the three similarity scores gets multiplied by its weight, they all get added together, and then the total is divided by the sum of the weights so every song ends up with a final score between 0.00 and 1.00:

```
final_score = (mood_score * mood_weight
             + genre_score * genre_weight
             + energy_score * energy_weight) / total_weight
```

After every song receives a score, the songs are sorted from highest to lowest, and the highest scoring songs are recommended first. All of this happens in ranking.py before Gemini is called at all. The agent receives only the 5 winners and writes the explanation for each one, and it is told in the prompt that it cannot reorder them, add or drop songs, or change any score.

This is the main thing I changed from my last version. Before, similarity was judged by the AI agent, which meant I couldn't see or test how it decided two genres were alike. Now the similarity is a number I can print, and the agent's judgement is only used for the wording.

---

## 4. Data 

Describe the dataset the model uses. 

The model reads from spotify_songs.csv, a catalog of about 100 songs adapted from a Spotify dataset. Each row represents one song and contains an id, the artist(s), the track name, an energy value between 0 and 1, a track genre, and a mood. Energy comes directly from Spotify's audio features, while the mood column was added to give the recommender something closer to a "vibe" to match against. I expanded and edited the original starter dataset so it would include a wider variety of genres, moods, and energy levels, since the recommender can only ever suggest songs that actually exist in this file. This means the quality of any recommendation is based on how diverse the data is.

How the data gets used also changed. It used to be that the entire CSV was uploaded to the Gemini agent as the RAG payload so it had every song to judge from. Now Python reads the CSV with pandas and does the searching, and only the 5 songs that won get sent to the agent, as CSV rows in chunks of 2 with the song id stripped out. The agent never sees the songs that lost. This dropped what I send from the whole dataset down to a few hundred tokens.

---

## 5. Limitations and Bias

Where the system struggles or behaves unfairly.

The biggest limitation is still the size of the catalog. The system can only recommend from around 100 songs, so users with niche tastes may not find a good match simply because the dataset doesn't contain one. Originally the dataset had 100,000+ songs but I had to narrow it down, because uploading the whole file to Gemini's API overloaded it and it would crash. That specific reason no longer applies now that the CSV never gets uploaded and Python does the searching, so the dataset could grow much larger than 100 songs. I just haven't expanded it back yet.

There is also bias in how the weights are assigned. Even though the user ranks which attributes matter most, I chose the actual weight values (6.0, 3.0, 1.0), because I wanted the recommendations to reflect the ranking so I decided the #1 ranking should dominate. That is my opinion about how much a user's top priority should matter, not the user's.

The similarity judgement used to be handed to the Gemini agent, which meant whatever bias the AI had about which genres or moods are "similar" showed up in the results, and I had no way to guarantee it was applying my weights at all. The same preferences could produce a different ranking each time. That's fixed now, but the bias just moved somewhere else. CountVectorizer only compares words, so it thinks "alt-rock" and "rock" are related but has no idea that "j-idol" and "pop" are, since they don't share a single word. Genres with a hyphen also get an advantage over one-word genres because they have more words available to match on, and single letters get ignored entirely, which is why "j-rock" scores a perfect 1.000 against "rock" instead of a partial one. So my scoring is consistent and testable, but it's biased toward genres that are spelled similarly rather than genres that actually sound similar.

Finally, there is no feedback loop, so the system never learns from a user's history or from why they chose to regenerate; that option is just open to the user if they choose to regenerate. Regenerating now returns the exact same 5 songs, since the ranking is deterministic. Only the wording of the explanations changes.

---

## 6. AI Misuse and Preventing it 

Since this system sends user preferences and song data to an external Gemini API, the main misuse risks come from what gets entered and what the AI is asked to do. A user could try to inject instructions into the preference fields to make the agent ignore the song data and produce unrelated or harmful output. To prevent this, the prompt in ranking.py is structured so the user's genre, mood, and energy are inserted as data rather than as open instructions.

Moving the scoring into Python helped here too. Since the agent no longer picks the songs, injected text in the genre or mood field can't change which songs get recommended, because those are already chosen before the agent is ever called. The genre and mood the user types only ever get used as input to CountVectorizer, so at worst a prompt injection produces a weird explanation next to a correct list of songs. The agent also only ever receives the 5 winning rows, so it can't be talked into recommending something outside the dataset because it doesn't have the rest of the dataset to pull from. On top of that, I ask it for JSON with only the explanation sentences, and the song title and score printed to the user come from my own DataFrame, so the agent can't change what score the user sees.

---

## 7. What surprised me

What surprised me most was how much of the judgement and results of the system was in the hands of AI. I expected the difficult part to be writing the scoring logic, but once the Gemini agent handled similarity, the tricky part became trusting it. My pytests all passed and confirmed the weights and prompt were correct, yet the recommendations could still feel off. This made me realize my tests could only prove the inputs were right and the prompt was getting the necessary information, not that the AI actually used them the way I wanted. I was also surprised at how easily bias showed up in such a simple system, and how the same exact preferences could produce slightly different results each time.

Then what surprised me going the other direction was how much simpler the fix was than I expected. I thought replacing the agent's judgement would mean writing a huge complicated backend, which is the exact thing I avoided by using an agent in the first place. It ended up being CountVectorizer and cosine_similarity, which is a handful of lines, and it gave me a similarity number for every song that I can look at and test. I also assumed giving the model more data would make it better. It did the opposite. Sending it the entire CSV overloaded it and forced me to cut my dataset down, and sending it 5 rows in chunks made the whole system both more reliable and able to handle a bigger dataset than before.

The bias didn't disappear though, it just moved. It used to be the AI's opinion about which genres sound alike, and now it's my vectorizer only being able to compare spelling. The difference is that this version I can actually see and explain, which is what I couldn't do before.

---

## 8. AI Collaboration and Reflection with Usage 

Working with the Gemini agent changed how I think about building these systems. At first, instead of writing strict backend code, I handed how genres and moods are judged as "similar" over to the AI and focused my own code on assigning weights and shaping the prompt. This made the system feel more flexible and closer to a real recommender, but it also meant I had to give up some control. The AI could take the same preferences and weights and still return slightly different results, which taught me that collaborating with an agent is less about writing perfect logic and more about guiding it and then trusting it to fill in the gaps.

The problem was that I was trusting it with the part I couldn't check. So I ended up dividing the work by what each side is actually good at. Python is good at math that has to come out the same every time, so it does the vectors, the cosine similarity, the weights, and the ranking. The agent is good at wording, so it writes the explanations. I even ask it for JSON with only the sentences, and the title and score in the final output come from my own DataFrame, so the layout is mine and the writing is its. Collaborating with an agent turned out to mean giving it a job small enough that I can tell when it's wrong, rather than fine-tuning it until I trust it with everything.

One instance where Claude gave me a helpful suggestion was when it helped me generate both "happy" cases and edge/unusual cases I could test in my pytests. At the time, I was struggling with how I would test the system because I couldn't test Gemini's output word-for-word (because it would always be slightly different). So Claude helped me generate manual tests that at least showed all the neccessary information was making it into the prompt. One instance where I got a flawed suggestion was when I asked for help on my diagram. At first, when I said the user could regenerate, the AI labeled it as "feedback" to the Gemini agent when regenerating. However, this didn't align with my system because it doesn't have history or know why the user is regenerating. It treats the regeneration as another generation.

When I rewrote the scoring, I also got a suggestion I had to push back on. Claude built the similarity with TF-IDF and a weight vector multiplied across a 2D matrix, which technically worked but wasn't what I asked for and made my own weighting system harder to see in the code. I asked for it to go back to my original weight logic and just swap the AI's judgement for cosine similarity, and the result was something I could actually read and explain. That was a good reminder that a suggestion working isn't the same as it being the right fit for my system.

The part that stuck with me most was the gap between testing the code and trusting the output. My pytests could prove the weights and prompt were correct, but they couldn't prove the AI applied them correctly and gave them more significance than its own thinking and judgements. The only real way to evaluate the recommendations was to look at them myself. Some questions I had to ask myself were if the top rank was dominating the way I intended? Is the AI still looking at the #2 and #3 rank to make decisions when the #1 rank no longer can? Now I can answer those questions with a test instead of a guess, because the scores are numbers I calculate. I realized how easy it was for bias to show up from my own dataset and weight choices, and that moving the scoring into Python didn't remove that bias, it just made it mine and made it visible. This made me appreciate why real recommendation systems rely on unique data, human review, and constant evaluation. Overall, integrating AI saved me from writing complex backend logic, but it also made me more aware that nowadays, in the world of AI, running perfect code without errors isn't the problem. It's making sure my intentions as a programmer are clear and the system behaves accordingly, because it can very much produce code that behaves differently from how I want.