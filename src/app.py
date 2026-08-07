import streamlit as st
from gemini import generate
from ranking import compute_weights, build_prefs, build_weights


# Page Configuration
st.set_page_config(page_title="AI DJ - Track Matcher", page_icon="🎵", layout="centered")


st.title("🎵 AI Music DJ: Recommends from your Preference")
st.write("Configure your song preferences and set your feature priorities for the active RAG engine.")


st.markdown("---")


# Ranking System (Click Order Logic)

st.subheader("1. Feature Priorities")
st.caption("Click the buttons in order of importance to you (1st Click = Top Priority).")


# Initialize session state for click ordering
if 'rank_order' not in st.session_state:
   st.session_state.rank_order = []


def register_click(feature):
   if feature not in st.session_state.rank_order:
       st.session_state.rank_order.append(feature)


def reset_ranks():
   st.session_state.rank_order = []


# Define specific colors and labels weights for each rank
RANK_STYLES = {
   1: {"label": "🥇 Rank 1 (Weight: 6.0)", "bg": "#E8F5E9", "border": "#2E7D32", "text": "#1B5E20"},  # Emerald Green
   2: {"label": "🥈 Rank 2 (Weight: 3.0)", "bg": "#E3F2FD", "border": "#1565C0", "text": "#0D47A1"},  # Sapphire Blue
   3: {"label": "🥉 Rank 3 (Weight: 1.0)", "bg": "#FFF3E0", "border": "#EF6C00", "text": "#E65100"},  # Amber/Bronze
}


features = ["Genre", "Mood", "Energy"]
col1, col2, col3 = st.columns(3)


for idx, feat in enumerate(features):
   target_col = [col1, col2, col3][idx]
  
   with target_col:
       if feat in st.session_state.rank_order:
           # Item is ranked -> display colored badge
           rank = st.session_state.rank_order.index(feat) + 1
           style = RANK_STYLES[rank]
          
           st.markdown(
               f"""
               <div style="
                   background-color: {style['bg']};
                   border: 2px solid {style['border']};
                   color: {style['text']};
                   border-radius: 10px;
                   padding: 15px;
                   text-align: center;
                   font-weight: bold;
               ">
                   <div style="font-size: 1.1rem;">{feat}</div>
                   <div style="font-size: 0.85rem; margin-top: 6px;">{style['label']}</div>
               </div>
               """,
               unsafe_allow_html=True
           )
       else:
           # Item not ranked yet -> clickable
           st.button(f"Prioritize {feat}", key=feat, on_click=register_click, args=(feat,), use_container_width=True)


# Status & Reset Controls
st.write("")
if st.session_state.rank_order:
   st.button("🔄 Reset Priorities", on_click=reset_ranks, type="secondary")


# Calculate weights based on ranks
weights = compute_weights(st.session_state.rank_order)
if len(st.session_state.rank_order) == 3:
   st.success(f"**Calculated Weights:** Genre: `{weights['genre']}` | Mood: `{weights['mood']}` | Energy: `{weights['energy']}`")
else:
   st.info(f"Click all 3 features above to lock in your weights. ({len(st.session_state.rank_order)}/3 ranked)")


st.markdown("---")



# User inputs their preferences

st.subheader("2. Target Preferences")


input_col1, input_col2 = st.columns(2)


with input_col1:
   preferred_genre = st.text_input(
       "Preferred Genre: "
   )
   preferred_mood = st.text_input(
       "Preferred Mood: "
   )


with input_col2:
   preferred_energy = st.slider(
       "Target Energy Level",
       min_value=0.0,
       max_value=1.0,
       value=0.85,
       step=0.05,
       help="0.0 = Acoustic/Calm, 1.0 = High Energy/Workout"
   )


st.markdown("---")



# Makes RAG payload from inputs

if st.button("🚀 Find Matching Songs", type="primary", use_container_width=True):
   if len(st.session_state.rank_order) < 3:
       st.error("Please click all 3 priority buttons before running the search!")
   else:
       st.subheader("3. Generated RAG Input Data")
      
       # Payload ready for the Gemini RAG backend pipeline
       prefs_payload = build_prefs(
           preferred_genre, preferred_mood, preferred_energy
       )
       weights_payload = build_weights(st.session_state.rank_order)


       st.json({**prefs_payload, **weights_payload})


       # Rank locally with cosine similarity, then let Gemini explain the result.
       st.subheader("4. Recommended Songs")
       with st.spinner("Scoring the catalog and asking the AI DJ to explain..."):
           try:
               explanation, recommended, token_count = generate(
                   prefs_payload, weights_payload
               )

               # The cosine scores below ARE the ranking -- show them first.
               st.dataframe(
                   recommended[[
                       "artists", "track_name", "track_genre", "mood", "energy",
                       "final_score", "genre_score", "mood_score", "energy_score",
                   ]],
                   hide_index=True,
                   use_container_width=True,
               )

               st.markdown(explanation)
               st.caption(f"Prompt sent to Gemini: {token_count} tokens.")
           except Exception as e:
               st.error(f"Recommendation failed: {e}")