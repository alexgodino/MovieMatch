from pathlib import Path
from difflib import SequenceMatcher

import pandas as pd
import streamlit as st


st.set_page_config(page_title="MovieMatch", layout="wide")


DATA_PATH = Path(__file__).with_name("movies.csv")
df = pd.read_csv(DATA_PATH)
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["runtime"] = pd.to_numeric(df["runtime"], errors="coerce")
df["imdb_rating"] = pd.to_numeric(df["imdb_rating"], errors="coerce")
df["your_rating"] = pd.to_numeric(df.get("your_rating"), errors="coerce")
df["plot_blurb"] = df.get("plot_blurb", "").fillna("").astype(str).str.strip()
df["genre"] = df["genre"].fillna("").str.strip()
df["title"] = df["title"].fillna("").str.strip()

GENRE_BUCKETS = [
    "Action",
    "Adventure",
    "Animation",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "Historical",
    "Horror",
    "Music",
    "Mystery",
    "Noir",
    "Romance",
    "Satire",
    "Sci-Fi",
    "Thriller",
    "War",
    "Western",
]

BASE_MOODS = [
    "Feel-Good",
    "Emotional",
    "Dark",
    "Intense",
    "Suspenseful",
    "Nostalgic",
    "Romantic",
    "Thought-Provoking",
    "Funny",
    "Epic",
]
MOOD_OPTIONS = ["Any mood"] + BASE_MOODS
GENRE_OPTIONS = ["Any genre"] + GENRE_BUCKETS
BASE_MOOD_TO_TAGS = {
    "Feel-Good": {"feel-good", "uplifting", "comforting", "heartwarming"},
    "Emotional": {"emotional", "moving", "bittersweet", "melancholic"},
    "Dark": {"dark", "bleak", "gritty", "haunting"},
    "Intense": {"intense", "adrenaline", "visceral", "chaotic"},
    "Suspenseful": {"suspenseful", "tense", "mysterious", "anxious"},
    "Nostalgic": {"nostalgic", "dreamy", "wistful", "reflective"},
    "Romantic": {"romantic", "tender", "yearning", "passionate"},
    "Thought-Provoking": {"thought-provoking", "cerebral", "existential", "mind-bending"},
    "Funny": {"funny", "witty", "playful", "goofy"},
    "Epic": {"epic", "grand", "awe-filled", "adventurous"},
}
GENRE_TO_TAGS = {
    "Action": {"adrenaline", "energetic"},
    "Adventure": {"adventurous", "epic"},
    "Animation": {"whimsical"},
    "Comedy": {"funny", "playful"},
    "Crime": {"gritty"},
    "Drama": {"character-driven"},
    "Fantasy": {"whimsical", "dreamy"},
    "Historical": {"reflective"},
    "Horror": {"haunting", "disturbing"},
    "Music": {"vibrant"},
    "Mystery": {"mysterious"},
    "Noir": {"moody", "gritty"},
    "Romance": {"romantic"},
    "Satire": {"sharp"},
    "Sci-Fi": {"futuristic", "tech-driven"},
    "Thriller": {"tense", "suspenseful"},
    "War": {"intense", "bleak"},
    "Western": {"rugged"},
}

SPECIFIC_MOOD_PROFILES = {
    "futuristic": {
        "keywords": ["futuristic", "future", "cyberpunk", "sci-fi", "technology", "tech-driven"],
        "fallback": "Thought-Provoking",
    },
    "existential": {
        "keywords": ["existential", "meaning", "purpose", "cosmic", "nihilism", "nihilistic"],
        "fallback": "Thought-Provoking",
    },
    "cozy": {
        "keywords": ["cozy", "comforting", "gentle", "warm", "soft"],
        "fallback": "Feel-Good",
    },
    "melancholic": {
        "keywords": ["melancholic", "aching", "lonely", "yearning", "wistful"],
        "fallback": "Emotional",
    },
    "surreal": {
        "keywords": ["surreal", "dreamlike", "uncanny", "strange", "disorienting"],
        "fallback": "Thought-Provoking",
    },
    "bleak": {
        "keywords": ["bleak", "grim", "despair", "hopeless", "depressing"],
        "fallback": "Dark",
    },
}

MOVIE_MOOD_TAGS = {
    ("2001: A Space Odyssey", 1968): {"existential"},
    ("After Yang", 2021): {"existential", "melancholic"},
    ("Blade Runner 2049", 2017): {"existential", "melancholic"},
    ("Dune", 2021): {"futuristic"},
    ("Dune: Part Two", 2024): {"futuristic"},
    ("Children of Men", 2006): {"existential", "bleak"},
    ("Donnie Darko", 2001): {"existential", "surreal"},
    ("Everything Everywhere All at Once", 2022): {"existential", "surreal"},
    ("Ex Machina", 2015): {"futuristic", "existential"},
    ("Her", 2013): {"existential", "melancholic"},
    ("Ikiru", 1952): {"existential"},
    ("Interstellar", 2014): {"futuristic", "awe-filled"},
    ("Memento", 2000): {"existential"},
    ("Minority Report", 2002): {"futuristic"},
    ("Solaris", 1972): {"existential"},
    ("Stalker", 1979): {"existential"},
    ("Synecdoche, New York", 2008): {"existential", "surreal", "bleak"},
    ("The Matrix", 1999): {"existential"},
    ("Project Hail Mary", 2026): {"futuristic", "awe-filled"},
    ("Arrival", 2016): {"futuristic", "existential"},
    ("Wings of Desire", 1987): {"existential", "melancholic"},
    ("Yi Yi", 2000): {"existential", "melancholic"},
    ("Aftersun", 2022): {"melancholic"},
    ("Blue Valentine", 2010): {"melancholic", "bleak"},
    ("Brief Encounter", 1945): {"melancholic"},
    ("Carol", 2015): {"melancholic"},
    ("In the Mood for Love", 2000): {"melancholic"},
    ("Manchester by the Sea", 2016): {"melancholic", "bleak"},
    ("Paris, Texas", 1984): {"melancholic"},
    ("Past Lives", 2023): {"melancholic"},
    ("Chef", 2014): {"cozy"},
    ("Fantastic Mr. Fox", 2009): {"cozy"},
    ("It's a Wonderful Life", 1946): {"cozy"},
    ("Kiki's Delivery Service", 1989): {"cozy"},
    ("Little Women", 2019): {"cozy"},
    ("My Neighbor Totoro", 1988): {"cozy"},
    ("Paddington 2", 2017): {"cozy"},
    ("Ratatouille", 2007): {"cozy"},
    ("The Holdovers", 2023): {"cozy"},
    ("Being John Malkovich", 1999): {"surreal"},
    ("Black Swan", 2010): {"surreal"},
    ("Mulholland Drive", 2001): {"surreal"},
    ("Perfect Blue", 1997): {"surreal"},
    ("Poor Things", 2023): {"surreal"},
    ("The Lighthouse", 2019): {"surreal"},
}
ALL_MOOD_TAGS = sorted(
    {
        tag
        for tags in BASE_MOOD_TO_TAGS.values()
        for tag in tags
    }
    | {
        tag
        for tags in GENRE_TO_TAGS.values()
        for tag in tags
    }
    | {
        tag
        for tags in MOVIE_MOOD_TAGS.values()
        for tag in tags
    }
)

MOOD_KEYWORDS = {
    "Feel-Good": ["happy", "uplifting", "cheerful", "comforting", "wholesome", "joyful", "warm"],
    "Emotional": ["sad", "moving", "cry", "crying", "grief", "heartbreaking", "poignant", "bittersweet"],
    "Dark": ["dark", "grim", "disturbing", "twisted", "brooding", "haunting"],
    "Intense": ["intense", "adrenaline", "stressful", "aggressive", "visceral", "brutal", "wild", "explosive"],
    "Suspenseful": ["tense", "suspenseful", "anxious", "thrilling", "mystery", "mysterious", "edge", "uneasy"],
    "Nostalgic": ["nostalgic", "wistful", "dreamy", "retro", "childhood", "throwback", "sentimental"],
    "Romantic": ["romantic", "love", "intimate", "yearning", "tender", "passionate", "date night"],
    "Thought-Provoking": ["thoughtful", "thought-provoking", "reflective", "philosophical", "cerebral", "mind-bending"],
    "Funny": ["funny", "hilarious", "goofy", "witty", "laugh", "laughing", "playful", "silly"],
    "Epic": ["epic", "grand", "sweeping", "majestic", "heroic", "adventurous", "larger-than-life"],
}


def matches_genre_bucket(movie_genre: str, selected_bucket: str) -> bool:
    genre_parts = [part.strip() for part in str(movie_genre).split("/")]
    return selected_bucket in genre_parts


def get_movie_details(title: str) -> pd.Series:
    return df.loc[df["title"] == title].iloc[0]


def get_movie_specific_tags(movie: pd.Series) -> set[str]:
    key = (movie["title"], int(movie["year"])) if pd.notna(movie["year"]) else (movie["title"], None)
    return MOVIE_MOOD_TAGS.get(key, set())


def get_movie_mood_tags(movie: pd.Series) -> set[str]:
    tags = set()
    base_mood = str(movie["mood"]).strip()
    tags.update(BASE_MOOD_TO_TAGS.get(base_mood, set()))
    tags.add(base_mood.lower())

    genre_parts = [part.strip() for part in str(movie["genre"]).split("/")]
    for part in genre_parts:
        tags.update(GENRE_TO_TAGS.get(part, set()))

    tags.update(get_movie_specific_tags(movie))
    return {tag for tag in tags if tag and tag.lower() != "nan"}


def infer_best_mood_tag(mood_text: str) -> tuple[str | None, float]:
    normalized_text = mood_text.strip().lower()
    if not normalized_text:
        return None, 0.0

    text_tokens = normalized_text.replace("-", " ").split()
    candidate_scores: list[tuple[str, float]] = []

    for tag in ALL_MOOD_TAGS:
        score = SequenceMatcher(None, normalized_text, tag).ratio()
        if any(token in tag or tag in token for token in text_tokens):
            score = max(score, 0.9)
        candidate_scores.append((tag, score))

    for tag, profile in SPECIFIC_MOOD_PROFILES.items():
        score = SequenceMatcher(None, normalized_text, tag).ratio()
        for keyword in profile["keywords"]:
            score = max(score, SequenceMatcher(None, normalized_text, keyword).ratio())
            if any(token in keyword or keyword in token for token in text_tokens):
                score = max(score, 0.92)
        candidate_scores.append((tag, score))

    best_tag, best_score = max(candidate_scores, key=lambda item: item[1])
    if best_score < 0.72:
        return None, best_score
    return best_tag, best_score


def infer_mood_from_text(custom_mood: str) -> tuple[str | None, float]:
    normalized_text = custom_mood.strip().lower()
    if not normalized_text:
        return None, 0.0

    text_tokens = normalized_text.replace("-", " ").split()
    best_mood = None
    best_score = 0.0

    for mood, keywords in MOOD_KEYWORDS.items():
        scores = []
        for keyword in keywords + [mood.lower()]:
            scores.append(SequenceMatcher(None, normalized_text, keyword).ratio())
            if any(token in keyword or keyword in token for token in text_tokens):
                scores.append(0.9)
        mood_score = max(scores)
        if mood_score > best_score:
            best_mood = mood
            best_score = mood_score

    if best_score < 0.75:
        return None, best_score

    return best_mood, best_score


def build_filtered_movies(
    mood_choice: str,
    genre_choice: str,
    typed_mood_tags: list[str] | None = None,
) -> pd.DataFrame:
    filtered = df.copy()
    if typed_mood_tags:
        tag_set = set(typed_mood_tags)
        filtered = filtered[filtered.apply(lambda row: tag_set.issubset(get_movie_mood_tags(row)), axis=1)]
    elif mood_choice != "Any mood":
        filtered = filtered[filtered["mood"] == mood_choice]
    if genre_choice != "Any genre":
        filtered = filtered[filtered["genre"].apply(lambda genre: matches_genre_bucket(genre, genre_choice))]
    return filtered.sort_values(
        by=["your_rating", "imdb_rating"],
        ascending=False,
        na_position="last",
    )


def select_defaults(movie_titles: list[str]) -> tuple[int, int]:
    if not movie_titles:
        return 0, 0
    if len(movie_titles) == 1:
        return 0, 0
    return 0, 1


def find_movie_index(movie_titles: list[str], title: str, fallback: int) -> int:
    if title in movie_titles:
        return movie_titles.index(title)
    return fallback


def sync_comparison_selection(selected_titles: list[str], available_titles: list[str]) -> None:
    if not selected_titles:
        return

    first_title = selected_titles[0]
    if first_title in available_titles:
        st.session_state["movie_1"] = first_title

    if len(selected_titles) >= 2:
        second_title = selected_titles[1]
    else:
        second_title = next((title for title in available_titles if title != first_title), first_title)

    if second_title in available_titles:
        st.session_state["movie_2"] = second_title


def build_story_preview(movie: pd.Series) -> str:
    if movie.get("plot_blurb"):
        return movie["plot_blurb"]
    genre = str(movie["genre"]).lower()
    mood = str(movie["mood"]).lower()
    return (
        f"A {mood} {genre} from {int(movie['year']) if pd.notna(movie['year']) else 'an unknown year'} directed by {movie['director']}. "
        f"It is the kind of film people usually reach for when they want a {mood} watch "
        f"with strong work from {movie['top_billed_actors']}."
    )


def display_value(value, decimals: int = 1) -> str:
    if pd.isna(value) or value == "":
        return "-"
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)


def format_runtime(minutes) -> str:
    if pd.isna(minutes) or minutes == "":
        return "-"
    total_minutes = int(minutes)
    hours = total_minutes // 60
    mins = total_minutes % 60
    return f"{hours}h {mins}m"


st.title("MovieMatch")
st.write(
    "Discover movies by mood and genre, then compare two picks side by side using ratings, runtime, cast, and crew details."
)

st.subheader("1. Find Your Matches")
filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    custom_mood = st.text_input(
        "Describe your mood in your own words",
        placeholder="Examples: futuristic or futuristic, adrenaline",
        help="Type one mood word or separate a couple with commas. MovieMatch will map that input onto its internal mood tags.",
    )
    mood_choice = st.selectbox(
        "Or choose a mood directly",
        MOOD_OPTIONS,
        index=0,
        help="Use this if you want to browse by one of the app's built-in moods.",
    )

with filter_col2:
    genre_choice = st.selectbox(
        "Optionally narrow by genre",
        GENRE_OPTIONS,
        help="Pairing mood with genre makes the results feel more targeted.",
    )

matched_mood = None
matched_typed_tags: list[str] = []
confidence = 0.0

if custom_mood.strip():
    typed_parts = [part.strip() for part in custom_mood.split(",") if part.strip()]
    typed_scores = []
    for part in typed_parts:
        matched_tag, part_confidence = infer_best_mood_tag(part)
        if matched_tag:
            matched_typed_tags.append(matched_tag)
            typed_scores.append(part_confidence)
        else:
            matched_typed_tags = []
            typed_scores = []
            break

    if not matched_typed_tags:
        matched_mood, confidence = infer_mood_from_text(custom_mood)
        if matched_mood:
            mood_choice = matched_mood
        else:
            st.warning(
                "I couldn't confidently match that mood yet. Try a more descriptive word or use the built-in mood list."
            )
    elif typed_scores:
        confidence = min(typed_scores)

filtered_movies = build_filtered_movies(mood_choice, genre_choice, matched_typed_tags)
display_mood_label = ", ".join(matched_typed_tags) if matched_typed_tags else mood_choice

st.write(
    f"Showing **{len(filtered_movies)}** movie(s)"
    + (f" for **{display_mood_label}**" if display_mood_label != "Any mood" else "")
    + (f" in **{genre_choice}**" if genre_choice != "Any genre" else "")
    + "."
)

if filtered_movies.empty and matched_typed_tags:
    st.warning(
        "No movies matched that typed mood combination in this genre, so try a different genre or a broader mood word."
    )
    comparison_pool = df.sort_values(by="title")
elif filtered_movies.empty:
    st.warning("No movies matched that mood and genre combination yet. Try a different genre or keep it on Any genre.")
    comparison_pool = df.sort_values(by="title")
else:
    discovery_table = filtered_movies[
        ["title", "year", "genre", "imdb_rating", "director", "rotten_tomatoes"]
    ].rename(
        columns={
            "title": "Title",
            "year": "Year",
            "genre": "Genre",
            "director": "Director",
            "imdb_rating": "IMDb Rating",
            "rotten_tomatoes": "Rotten Tomatoes",
        }
    )
    discovery_table["IMDb Rating"] = discovery_table["IMDb Rating"].apply(display_value)
    discovery_table["Rotten Tomatoes"] = discovery_table["Rotten Tomatoes"].replace({"": "-", "nan": "-"}).fillna("-")
    discovery_table["Director"] = discovery_table["Director"].replace({"": "-", "Not added yet": "-"}).fillna("-")
    discovery_table.insert(0, "Compare", False)
    edited_table = st.data_editor(
        discovery_table,
        width="stretch",
        hide_index=True,
        disabled=["Title", "Year", "Genre", "IMDb Rating", "Director", "Rotten Tomatoes"],
        column_config={
            "Compare": st.column_config.CheckboxColumn(
                "Compare",
                help="Check up to two movies to send them straight to the comparison section.",
            )
        },
        key="discovery_compare_table",
    )
    comparison_pool = filtered_movies
    quick_compare_titles = edited_table.loc[edited_table["Compare"], "Title"].tolist()[:2]

comparison_titles = comparison_pool["title"].tolist()
default_index_1, default_index_2 = select_defaults(comparison_titles)

if not filtered_movies.empty:
    if len(quick_compare_titles) >= 1:
        default_index_1 = find_movie_index(comparison_titles, quick_compare_titles[0], default_index_1)
    if len(quick_compare_titles) >= 2:
        default_index_2 = find_movie_index(comparison_titles, quick_compare_titles[1], default_index_2)
    elif len(quick_compare_titles) == 1 and len(comparison_titles) > 1:
        fallback_second = next((title for title in comparison_titles if title != quick_compare_titles[0]), comparison_titles[0])
        default_index_2 = find_movie_index(comparison_titles, fallback_second, default_index_2)
    sync_comparison_selection(quick_compare_titles, comparison_titles)

st.subheader("2. Compare Movies From Your Results")
st.caption("Check up to two movies in the results table above to send them here instantly. If a filter returns nothing, the app falls back to the full list so you can keep exploring.")

compare_col1, compare_col2 = st.columns(2)

with compare_col1:
    movie_1_title = st.selectbox(
        "Choose your first movie",
        comparison_titles,
        index=default_index_1,
        key="movie_1",
    )

with compare_col2:
    movie_2_title = st.selectbox(
        "Choose your second movie",
        comparison_titles,
        index=default_index_2,
        key="movie_2",
    )

movie_1 = get_movie_details(movie_1_title)
movie_2 = get_movie_details(movie_2_title)

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    with st.popover(f"Story preview: {movie_1_title}"):
        st.write(build_story_preview(movie_1))

with summary_col2:
    with st.popover(f"Story preview: {movie_2_title}"):
        st.write(build_story_preview(movie_2))

comparison_table = pd.DataFrame(
    {
        "Attribute": [
            "Year",
            "Mood",
            "Genre",
            "Director",
            "Top billed actors",
            "Composer",
            "Cinematographer",
            "Runtime (minutes)",
            "IMDb rating",
            "Rotten Tomatoes",
        ],
        movie_1_title: [
            display_value(movie_1["year"], 0),
            display_value(movie_1["mood"], 0),
            display_value(movie_1["genre"], 0),
            display_value(movie_1["director"], 0).replace("Not added yet", "-"),
            display_value(movie_1["top_billed_actors"], 0).replace("Not added yet", "-"),
            display_value(movie_1["composer"], 0).replace("Not added yet", "-"),
            display_value(movie_1["cinematographer"], 0).replace("Not added yet", "-"),
            format_runtime(movie_1["runtime"]),
            display_value(movie_1["imdb_rating"]),
            display_value(movie_1["rotten_tomatoes"], 0),
        ],
        movie_2_title: [
            display_value(movie_2["year"], 0),
            display_value(movie_2["mood"], 0),
            display_value(movie_2["genre"], 0),
            display_value(movie_2["director"], 0).replace("Not added yet", "-"),
            display_value(movie_2["top_billed_actors"], 0).replace("Not added yet", "-"),
            display_value(movie_2["composer"], 0).replace("Not added yet", "-"),
            display_value(movie_2["cinematographer"], 0).replace("Not added yet", "-"),
            format_runtime(movie_2["runtime"]),
            display_value(movie_2["imdb_rating"]),
            display_value(movie_2["rotten_tomatoes"], 0),
        ],
    }
).astype(str)
st.dataframe(comparison_table, width="stretch", hide_index=True)

if movie_1_title != movie_2_title:
    higher_imdb = movie_1_title if movie_1["imdb_rating"] >= movie_2["imdb_rating"] else movie_2_title
    shorter_runtime = movie_1_title if movie_1["runtime"] <= movie_2["runtime"] else movie_2_title
    st.markdown(
        f"**Quick take:** `{higher_imdb}` leads on IMDb, and `{shorter_runtime}` is the shorter watch."
    )
