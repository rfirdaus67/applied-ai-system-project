# 🎧 Model Card: Music Recommender Simulation

---

## 1. Model Name 


Give your model a short, descriptive name. 


Name: AI Music DJ

---

## 2. Intended Use 

Describe what your recommender is designed to do and who it is for.

The AI Music DJ is a program designed to generate song recommendations based on your preferences, whether it be by mood, genre, or energy. It lets the user input their preferred genre(s), mood(s), and energy level and rank which one is most important to them. Then these preferences are fed into a Gemini agent that assigns a score to each song. Then the songs are ranked from highest to lowest score, highest meaning the song best matches the user.

---

## 3. How the Model Works 

Explain your scoring approach in simple language. 

Each song has three attributes taken into account: genre, mood, and energy. The user is able to input a preferred genre, mood, and energy level and rank them for their recommendations. For every song in the catalog, the recommender compares these features against the user's preferences.

Genre and mood are added to the score it is an exact match or similar. Similarity is judged by the AI agent. Energy is compared numerically by measuring how close the song's energy is to the user's preferred energy. Whichever attribute is ranked #1 has the highest weight (6.0), #2 ranked is weighted second (3.0), and #3 ranked is weighted third (1.0). After every song receives a score, the songs are sorted from highest to lowest, and the highest scoring songs are recommended first.

---

## 4. Data 

Describe the dataset the model uses. 

The model reads from spotify_songs.csv, a catalog of about 100 songs adapted from a Spotify dataset. Each row represents one song and contains an id, the artist(s), the track name, an energy value between 0 and 1, a track genre, and a mood. Energy comes directly from Spotify's audio features, while the mood column was added to give the recommender something closer to a "vibe" to match against. I expanded and edited the original starter dataset so it would include a wider variety of genres, moods, and energy levels, since the recommender can only ever suggest songs that actually exist in this file. This means the quality of any recommendation is based on how diverse the data is. The whole data, along with the user's preferences and assigned weights, is passed into the Gemini agent as a RAG payload so the agent has multiple songs to judge from.

---

## 5. Limitations and Bias

Where the system struggles or behaves unfairly.

The biggest limitation is that the system can only recommend from a small catalog of around 100 songs, so users with niche tastes may not find a good match simply because the dataset doesn't contain one. This is because of Gemini's API, as it can only read through a certain amount of data before crashing. Originally, the dataset had 100,000+ songs but I had to narrow it down to 100 songs. However, this is also the benefit of the system being able to use Gemini to find similar moods/genres if there isn't an exact match. There is also bias in how the weights are assigned. Even though the user ranks which attributes matter most, I chose the actual weight values (6.0, 3.0, 1.0), because I wanted the recommendations to reflect the ranking so I decided the #1 ranking should dominate. On top of that, I hand the similarity judgement to the Gemini agent, so whatever bias the AI has about which genres or moods are "similar" is reflected in the results. I can send the weights and ranking logic of attributes into the prompt, but I have no way to guarantee the AI actually applies them consistently and how much of its judgement it's using. This means the same preferences can produce slightly different rankings each time. Finally, there is no feedback loop, so the system never learns from a user's history or from why they chose to regenerate; that option is just open to the user if they choose to regenerate.

---

## 6. AI Misuse and Preventing it 

Since this system sends user preferences and a song catalog to an external Gemini API, the main misuse risks come from what gets entered and what the AI is asked to do. A user could try to inject instructions into the preference fields to make the agent ignore the song data and produce unrelated or harmful output. To prevent this, the prompt in ranking.py is structured so the user's genre, mood, and energy are inserted as data rather than as open instructions, and the agent is told specifically to only recommend songs from the provided dataset.

---

## 7. What surprised me

What surprised me most was how much of the judgement and results of the system is in the hands of AI. I expected the difficult part to be writing the scoring logic, but once the Gemini agent handled similarity, the tricky part became trusting it. Normally, when you use AI, its output is explained in detail. However, using the API and only outputting the information I need while reducing the explanation part makes AI's judgement unknown to me and the user. My pytests all passed and confirmed the weights and prompt were correct, yet the recommendations could still feel off. This made me realize my tests could only prove the inputs were right and the prompt was getting the necessary information, not that the AI actually used them the way I wanted. I was also surprised at how easily bias showed up in such a simple system, and how the same exact preferences could produce slightly different results each time. There's definitely a gap in my understanding of how AI is making judgements outside of the prompt it's given, but this is something that could be investigated upon with more tests in the future.

---

## 8. AI Collaboration and Reflection with Usage 

Working with the Gemini agent changed how I think about building these systems. Instead of writing strict backend code, I handed how genres and moods are judged as "similar" over to the AI and focused my own code on assigning weights and shaping the prompt. This made the system feel more flexible and closer to a real recommender, but it also meant I had to give up some control. The AI could take the same preferences and weights and still return slightly different results, which taught me that collaborating with an agent is less about writing perfect logic and more about guiding it and then trusting it to fill in the gaps. However, as the creator, I still need to do more testing to ensure I know exactly what AI is doing every step of the way. Maybe this means fine-tuning the model more or using a more advanced model so it behaves more closely to how I want.

The part that stuck with me most was the gap between testing the code and trusting the output. My pytests could prove the weights and prompt were correct, but they couldn't prove the AI applied them correctly and gave them more significance than its own thinking and judgements. The only real way to evaluate the recommendations was to look at them myself. Some questions I had to ask myself were if the top rank was dominating the way I intended? Is the AI still looking at the #2 and #3 rank to make decisions when the #1 rank no longer can? I also had to play around with different inputs like if I was allowed to input multiple genres and moods. I realized how easy it was for bias to show up from my own dataset and weight choices and this made me appreciate why real recommendation systems rely on unique data, human review, and constant evaluation. Overall, integrating AI saved me from writing complex backend logic, but it also made me more aware that nowadays, in the world of AI, running perfect code without errors isn't the problem. It's making sure my intentions as a programmer are clear and the system behaves accordingly, because it can very much produce code that behaves differently from how I want.