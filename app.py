import re
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="MovieMatch", layout="wide")


DATA_PATH = Path(__file__).with_name("movies.csv")
TEXT_COLUMNS = [
    "title",
    "mood",
    "genre",
    "director",
    "top_billed_actors",
    "composer",
    "cinematographer",
    "rotten_tomatoes",
    "plot_blurb",
]
NUMERIC_COLUMNS = ["year", "runtime", "imdb_rating", "letterboxd_rating", "your_rating"]
OPTIONAL_COLUMNS = ["plot_blurb", "your_rating"]

GENRE_BUCKETS = [
    "Action",
    "Adventure",
    "Animation",
    "Biography",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "History",
    "Horror",
    "Music",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Sport",
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
DEFAULT_KEYS = {
    "custom_mood_input": "",
    "mood_choice": "Any mood",
    "genre_choice": "Any genre",
    "title_search": "",
}
STRICT_POSITIVE_TERMS = {"happy", "uplifting", "cheerful", "joyful", "feel good", "feel-good"}

BASE_MOOD_TO_TAGS = {
    "Feel-Good": {"comforting", "uplifting", "warm", "playful"},
    "Emotional": {"melancholic", "moving", "tender", "reflective"},
    "Dark": {"dark", "gritty", "haunting", "bleak"},
    "Intense": {"intense", "adrenaline", "visceral", "chaotic"},
    "Suspenseful": {"suspenseful", "tense", "mysterious", "anxious"},
    "Nostalgic": {"nostalgic", "dreamy", "wistful", "reflective"},
    "Romantic": {"romantic", "tender", "yearning", "beautiful"},
    "Thought-Provoking": {"cerebral", "reflective", "existential", "mind-bending"},
    "Funny": {"funny", "witty", "playful", "offbeat"},
    "Epic": {"epic", "grand", "adventurous", "awe-filled"},
}
GENRE_TO_TAGS = {
    "Action": {"adrenaline", "intense"},
    "Adventure": {"adventurous", "epic"},
    "Animation": {"playful", "whimsical"},
    "Biography": {"reflective"},
    "Comedy": {"funny", "witty"},
    "Crime": {"gritty", "dark"},
    "Documentary": {"reflective"},
    "Drama": {"character-driven", "moving"},
    "Family": {"comforting", "warm"},
    "Fantasy": {"dreamy", "whimsical"},
    "History": {"reflective", "epic"},
    "Horror": {"haunting", "dark"},
    "Music": {"vibrant", "beautiful"},
    "Mystery": {"mysterious", "suspenseful"},
    "Romance": {"romantic", "tender"},
    "Sci-Fi": {"futuristic", "cerebral"},
    "Sport": {"uplifting", "intense"},
    "Thriller": {"tense", "suspenseful"},
    "War": {"bleak", "epic"},
    "Western": {"rugged", "adventurous"},
}
INTERNAL_TAG_SYNONYMS = {
    "comforting": ["comforting", "cozy", "cosy", "warm", "gentle", "wholesome", "soft"],
    "uplifting": ["uplifting", "feel good", "feel-good", "joyful", "cheerful"],
    "melancholic": ["sad", "melancholic", "bittersweet", "heartbreaking", "aching", "lonely"],
    "reflective": ["reflective", "thoughtful", "contemplative", "introspective", "meditative"],
    "dreamy": ["dreamy", "lush", "ethereal", "wistful", "beautiful"],
    "nostalgic": ["nostalgic", "retro", "throwback", "childhood", "sentimental"],
    "dark": ["dark", "grim", "brooding", "moody", "shadowy"],
    "bleak": ["bleak", "hopeless", "despairing", "grim", "devastating"],
    "funny": ["funny", "comedic", "hilarious", "laugh", "laughing", "humorous"],
    "witty": ["witty", "sharp", "clever", "dry", "snappy"],
    "surreal": ["surreal", "weird", "strange", "odd", "uncanny", "dreamlike"],
    "futuristic": ["futuristic", "future", "cyberpunk", "sci fi", "sci-fi", "science fiction", "techy"],
    "intense": ["intense", "visceral", "wild", "explosive", "aggressive", "high stakes"],
    "adrenaline": ["adrenaline", "thrill ride", "pulse pounding", "fast paced", "action packed"],
    "suspenseful": ["suspenseful", "thrilling", "tense", "edge of your seat", "nerve-racking"],
    "mysterious": ["mysterious", "enigmatic", "puzzling", "unknown"],
    "romantic": ["romantic", "in love", "date night", "passionate", "swoony"],
    "tender": ["tender", "sweet", "sincere", "beautiful", "gentle"],
    "epic": ["epic", "grand", "sweeping", "majestic", "larger than life"],
    "adventurous": ["adventurous", "journey", "quest", "exploratory", "escapist"],
    "cerebral": ["cerebral", "smart", "mind bending", "mind-bending", "philosophical"],
    "existential": ["existential", "meaning of life", "cosmic", "identity", "purpose"],
    "haunting": ["haunting", "eerie", "chilling", "unsettling", "disturbing"],
    "offbeat": ["offbeat", "quirky", "eccentric", "strange but funny"],
    "playful": ["playful", "light", "breezy", "energetic"],
}
MOVIE_MOOD_TAGS = {
    ("2001: A Space Odyssey", 1968): {"existential", "cerebral"},
    ("After Yang", 2021): {"existential", "reflective", "melancholic"},
    ("Aftersun", 2022): {"melancholic", "reflective", "beautiful"},
    ("Arrival", 2016): {"futuristic", "cerebral", "reflective"},
    ("Being John Malkovich", 1999): {"surreal", "offbeat"},
    ("Blade Runner 2049", 2017): {"futuristic", "existential", "dreamy"},
    ("Blue Valentine", 2010): {"melancholic", "bleak"},
    ("Carol", 2015): {"romantic", "tender", "beautiful"},
    ("Chef", 2014): {"comforting", "uplifting"},
    ("Children of Men", 2006): {"bleak", "intense", "futuristic"},
    ("Donnie Darko", 2001): {"surreal", "dark", "existential"},
    ("Dune", 2021): {"futuristic", "epic"},
    ("Dune: Part Two", 2024): {"futuristic", "epic", "intense"},
    ("Everything Everywhere All at Once", 2022): {"surreal", "funny", "existential"},
    ("Ex Machina", 2015): {"futuristic", "dark", "cerebral"},
    ("Fantastic Mr. Fox", 2009): {"comforting", "witty", "playful"},
    ("Her", 2013): {"melancholic", "romantic", "futuristic"},
    ("In the Mood for Love", 2000): {"melancholic", "romantic", "beautiful"},
    ("Interstellar", 2014): {"futuristic", "epic", "awe-filled"},
    ("It's a Wonderful Life", 1946): {"comforting", "uplifting"},
    ("Kiki's Delivery Service", 1989): {"comforting", "playful", "dreamy"},
    ("Little Women", 2019): {"comforting", "nostalgic", "tender"},
    ("Manchester by the Sea", 2016): {"melancholic", "bleak"},
    ("Mulholland Drive", 2001): {"surreal", "mysterious", "dreamy"},
    ("My Neighbor Totoro", 1988): {"comforting", "dreamy", "nostalgic"},
    ("Paddington 2", 2017): {"comforting", "uplifting", "funny"},
    ("Paris, Texas", 1984): {"melancholic", "reflective"},
    ("Past Lives", 2023): {"melancholic", "reflective", "romantic"},
    ("Perfect Blue", 1997): {"surreal", "haunting", "intense"},
    ("Poor Things", 2023): {"surreal", "funny", "adventurous"},
    ("Ratatouille", 2007): {"comforting", "uplifting", "playful"},
    ("Solaris", 1972): {"existential", "dreamy"},
    ("Stalker", 1979): {"existential", "reflective", "bleak"},
    ("Synecdoche, New York", 2008): {"existential", "surreal", "bleak"},
    ("The Holdovers", 2023): {"comforting", "funny", "nostalgic"},
    ("The Lighthouse", 2019): {"surreal", "haunting", "dark"},
    ("The Matrix", 1999): {"futuristic", "existential", "adrenaline"},
    ("Wings of Desire", 1987): {"dreamy", "reflective", "melancholic"},
    ("Yi Yi", 2000): {"reflective", "melancholic"},
}
TAG_LABELS = {
    "comforting": "comforting",
    "uplifting": "uplifting",
    "melancholic": "melancholic",
    "reflective": "reflective",
    "dreamy": "dreamy",
    "nostalgic": "nostalgic",
    "dark": "dark",
    "bleak": "bleak",
    "funny": "funny",
    "witty": "witty",
    "surreal": "surreal",
    "futuristic": "futuristic",
    "intense": "intense",
    "adrenaline": "adrenaline-fueled",
    "suspenseful": "suspenseful",
    "mysterious": "mysterious",
    "romantic": "romantic",
    "tender": "tender",
    "epic": "epic",
    "adventurous": "adventurous",
    "cerebral": "cerebral",
    "existential": "existential",
    "haunting": "haunting",
    "offbeat": "offbeat",
    "playful": "playful",
    "beautiful": "beautiful",
    "character-driven": "character-driven",
    "moving": "moving",
    "warm": "warm",
    "gritty": "gritty",
    "anxious": "anxious",
    "chaotic": "chaotic",
    "awe-filled": "awe-filled",
    "yearning": "yearning",
    "visceral": "visceral",
    "whimsical": "whimsical",
    "vibrant": "vibrant",
    "rugged": "rugged",
    "mind-bending": "mind-bending",
}


def normalize_text(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s-]", " ", str(text).lower())
    return re.sub(r"\s+", " ", cleaned.replace("-", " ")).strip()


def pretty_tag(tag: str) -> str:
    return TAG_LABELS.get(tag, tag.replace("-", " "))


def safe_text(value, fallback: str = "") -> str:
    if pd.isna(value):
        return fallback
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return fallback
    return text


def safe_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def make_movie_label(title: str, year) -> str:
    year_text = str(int(year)) if pd.notna(year) else "Unknown Year"
    return f"{safe_text(title, 'Untitled')} ({year_text})"


def parse_genres(value: str) -> list[str]:
    return [part.strip() for part in safe_text(value).split("/") if part.strip()]


def build_movie_specific_tags(title: str, year) -> set[str]:
    key = (title, int(year)) if pd.notna(year) else (title, None)
    return set(MOVIE_MOOD_TAGS.get(key, set()))


def get_movie_tags(row: pd.Series) -> set[str]:
    tags: set[str] = set()
    mood = safe_text(row.get("mood"))
    if mood and mood != "Uncategorized":
        tags.add(normalize_text(mood))
        tags.update(BASE_MOOD_TO_TAGS.get(mood, set()))

    for genre in row.get("genre_list", []):
        tags.add(normalize_text(genre))
        tags.update(GENRE_TO_TAGS.get(genre, set()))

    tags.update(build_movie_specific_tags(safe_text(row.get("title")), row.get("year")))
    return {tag for tag in tags if tag}


@st.cache_data(show_spinner=False)
def load_movie_data(csv_path: str) -> pd.DataFrame:
    movies = pd.read_csv(csv_path)

    for column in TEXT_COLUMNS:
        if column not in movies.columns:
            movies[column] = ""
    for column in OPTIONAL_COLUMNS:
        if column not in movies.columns:
            movies[column] = pd.NA
    for column in NUMERIC_COLUMNS:
        if column not in movies.columns:
            movies[column] = pd.NA

    for column in TEXT_COLUMNS:
        movies[column] = movies[column].fillna("").astype(str).str.strip()
    for column in NUMERIC_COLUMNS:
        movies[column] = safe_number(movies[column])

    movies["title"] = movies["title"].replace("", "Untitled")
    movies["mood"] = movies["mood"].replace("", "Uncategorized")
    movies["genre_list"] = movies["genre"].apply(parse_genres)
    movies["comparison_label"] = movies.apply(lambda row: make_movie_label(row["title"], row["year"]), axis=1)
    movies["search_title"] = movies["title"].str.lower()
    movies["curator_score"] = movies["your_rating"].fillna(0)
    movies["movie_tags"] = movies.apply(get_movie_tags, axis=1)
    return movies


def reset_filters() -> None:
    for key, value in DEFAULT_KEYS.items():
        st.session_state[key] = value
    for key in ["discovery_compare_table", "movie_1", "movie_2", "compare_selection_order", "compare_checked_labels"]:
        st.session_state.pop(key, None)


def split_mood_phrases(text: str) -> list[str]:
    normalized = normalize_text(text)
    if not normalized:
        return []
    pieces = re.split(r",|/|\band\b|\bbut\b|\bplus\b|\bwith\b", normalized)
    ordered = [normalized]
    ordered.extend(piece.strip() for piece in pieces if piece.strip())
    unique_phrases: list[str] = []
    for phrase in ordered:
        if phrase and phrase not in unique_phrases:
            unique_phrases.append(phrase)
    return unique_phrases


def infer_user_mood_tags(text: str) -> list[str]:
    tag_scores: dict[str, float] = {}
    phrases = split_mood_phrases(text)
    if not phrases:
        return []

    for phrase in phrases:
        phrase_tokens = set(phrase.split())
        for tag, synonyms in INTERNAL_TAG_SYNONYMS.items():
            candidates = [normalize_text(tag), *(normalize_text(item) for item in synonyms)]
            best_score = 0.0
            for candidate in candidates:
                if phrase == candidate:
                    best_score = 1.0
                    break
                if candidate in phrase or phrase in candidate:
                    best_score = max(best_score, 0.92)
                    continue
                candidate_tokens = set(candidate.split())
                overlap = len(phrase_tokens & candidate_tokens)
                if overlap and overlap == min(len(phrase_tokens), len(candidate_tokens)):
                    best_score = max(best_score, 0.87)
            if best_score >= 0.87:
                tag_scores[tag] = max(tag_scores.get(tag, 0.0), best_score)

    if not tag_scores:
        fuzzy_candidates = {
            normalize_text(candidate): tag
            for tag, synonyms in INTERNAL_TAG_SYNONYMS.items()
            for candidate in [tag, *synonyms]
        }
        for phrase in phrases:
            best_tag = None
            best_score = 0.0
            for candidate, tag in fuzzy_candidates.items():
                score = SequenceMatcher(None, phrase, candidate).ratio()
                if score > best_score:
                    best_tag = tag
                    best_score = score
            if best_tag and best_score >= 0.78:
                tag_scores[best_tag] = max(tag_scores.get(best_tag, 0.0), best_score)

    return [
        tag
        for tag, _score in sorted(tag_scores.items(), key=lambda item: (-item[1], pretty_tag(item[0])))
    ][:5]


def is_strict_positive_request(text: str) -> bool:
    phrases = split_mood_phrases(text)
    if not phrases:
        return False
    return len(phrases) == 1 and phrases[0] in STRICT_POSITIVE_TERMS


def genre_matches(genre_list: list[str], selected_genre: str) -> bool:
    return selected_genre == "Any genre" or selected_genre in genre_list


def broad_mood_bonus(tags: set[str], mood_choice: str) -> int:
    if mood_choice == "Any mood":
        return 0
    return len(tags & BASE_MOOD_TO_TAGS.get(mood_choice, set())) + int(normalize_text(mood_choice) in tags)


def search_movies(
    movies: pd.DataFrame,
    custom_mood_text: str,
    mood_choice: str,
    genre_choice: str,
    title_query: str,
) -> tuple[pd.DataFrame, list[str]]:
    filtered = movies.copy()

    if title_query.strip():
        query = title_query.strip().lower()
        filtered = filtered[filtered["search_title"].str.contains(query, na=False)]

    if genre_choice != "Any genre":
        filtered = filtered[filtered["genre_list"].apply(lambda genres: genre_matches(genres, genre_choice))]

    interpreted_tags = infer_user_mood_tags(custom_mood_text)

    if interpreted_tags:
        filtered["match_score"] = filtered["movie_tags"].apply(lambda tags: len(set(interpreted_tags) & tags))
        filtered["mood_bonus"] = filtered["movie_tags"].apply(lambda tags: broad_mood_bonus(tags, mood_choice))
        filtered = filtered[filtered["match_score"] > 0]
        if is_strict_positive_request(custom_mood_text):
            positive_tags = {"uplifting", "comforting", "playful", "funny", "warm"}
            filtered["positive_score"] = filtered["movie_tags"].apply(lambda tags: len(tags & positive_tags))
            filtered = filtered[
                (filtered["positive_score"] > 0)
                & (~filtered["movie_tags"].apply(lambda tags: bool(tags & {"bleak", "dark", "haunting"})))
            ]
        else:
            filtered["positive_score"] = 0
        filtered["why_it_fits"] = filtered["movie_tags"].apply(
            lambda tags: ", ".join(pretty_tag(tag) for tag in interpreted_tags if tag in tags)
        )
        filtered = filtered.sort_values(
            by=["match_score", "positive_score", "mood_bonus", "curator_score", "imdb_rating", "title"],
            ascending=[False, False, False, False, False, True],
            na_position="last",
        )
        return filtered, interpreted_tags

    if mood_choice != "Any mood":
        filtered = filtered[filtered["mood"] == mood_choice]

    filtered["match_score"] = 0
    filtered["mood_bonus"] = 0
    filtered["positive_score"] = 0
    filtered["why_it_fits"] = ""
    filtered = filtered.sort_values(
        by=["curator_score", "imdb_rating", "title"],
        ascending=[False, False, True],
        na_position="last",
    )
    return filtered, interpreted_tags


def display_value(value, decimals: int = 1) -> str:
    if pd.isna(value) or value == "":
        return "-"
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)


def format_runtime(minutes) -> str:
    if pd.isna(minutes):
        return "-"
    total_minutes = int(minutes)
    hours = total_minutes // 60
    mins = total_minutes % 60
    return f"{hours}h {mins}m"


def clean_credit(value) -> str:
    text = safe_text(value, "-")
    if text == "Not added yet":
        return "-"
    return text


def build_story_preview(movie: pd.Series) -> str:
    plot_blurb = safe_text(movie.get("plot_blurb"))
    if plot_blurb:
        return plot_blurb

    title = safe_text(movie.get("title"), "This film")
    mood = safe_text(movie.get("mood"), "character-driven").lower()
    genre = safe_text(movie.get("genre"), "drama").lower()
    director = clean_credit(movie.get("director"))
    cast = clean_credit(movie.get("top_billed_actors"))
    year = display_value(movie.get("year"), 0)
    return (
        f"{title} is a {mood} {genre} from {year}. "
        f"It is directed by {director} and features {cast}."
    )


def build_discovery_table(results: pd.DataFrame, interpreted_tags: list[str]) -> pd.DataFrame:
    columns = ["comparison_label", "title", "year", "genre", "imdb_rating", "director", "rotten_tomatoes"]
    if interpreted_tags:
        columns.append("why_it_fits")

    table = results[columns].copy()
    table.rename(
        columns={
            "title": "Title",
            "year": "Year",
            "genre": "Genre",
            "director": "Director",
            "imdb_rating": "IMDb Rating",
            "rotten_tomatoes": "Rotten Tomatoes",
            "why_it_fits": "Why It Fits",
        },
        inplace=True,
    )
    table["Title"] = table["comparison_label"]
    table.drop(columns=["comparison_label"], inplace=True)
    table["IMDb Rating"] = table["IMDb Rating"].apply(display_value)
    table["Director"] = table["Director"].apply(clean_credit)
    table["Rotten Tomatoes"] = table["Rotten Tomatoes"].replace({"": "-", "nan": "-"}).fillna("-")
    table.insert(0, "Compare", False)
    selected_labels = set(st.session_state.get("compare_selection_order", []))
    table["Compare"] = table["Title"].isin(selected_labels)
    return table


def handle_compare_editor_change(row_labels: list[str]) -> None:
    widget_state = st.session_state.get("discovery_compare_table", {})
    edited_rows = widget_state.get("edited_rows", {})
    current_order = [
        label for label in st.session_state.get("compare_selection_order", []) if label in row_labels
    ]

    for row_index, changes in edited_rows.items():
        if "Compare" not in changes:
            continue
        label = row_labels[int(row_index)]
        if changes["Compare"]:
            if label in current_order:
                current_order.remove(label)
            current_order.append(label)
        else:
            current_order = [item for item in current_order if item != label]

    current_order = current_order[-2:]
    st.session_state["compare_selection_order"] = current_order
    st.session_state["compare_checked_labels"] = current_order[:]
    widget_state["edited_rows"] = {}


def ensure_comparison_selection(pool: pd.DataFrame, preferred_labels: list[str]) -> tuple[str | None, str | None]:
    labels = pool["comparison_label"].tolist()
    if not labels:
        return None, None

    first_label = preferred_labels[0] if preferred_labels and preferred_labels[0] in labels else labels[0]
    second_options = [label for label in labels if label != first_label] or [first_label]

    if len(preferred_labels) > 1 and preferred_labels[1] in second_options:
        second_label = preferred_labels[1]
    else:
        current_second = st.session_state.get("movie_2")
        second_label = current_second if current_second in second_options else second_options[0]

    st.session_state["movie_1"] = first_label
    st.session_state["movie_2"] = second_label
    return first_label, second_label


def get_movie_by_label(pool: pd.DataFrame, label: str) -> pd.Series:
    return pool.loc[pool["comparison_label"] == label].iloc[0]


def describe_accessibility(movie: pd.Series) -> str:
    tags = movie.get("movie_tags", set())
    mood = safe_text(movie.get("mood"))
    if tags & {"comforting", "uplifting", "playful", "funny"} or mood in {"Feel-Good", "Funny"}:
        return "more immediately accessible"
    if tags & {"existential", "cerebral", "bleak", "haunting", "surreal"} or mood in {"Dark", "Thought-Provoking"}:
        return "more demanding"
    return "a middle-ground watch"


def build_quick_take(movie_1: pd.Series, movie_2: pd.Series, label_1: str, label_2: str) -> str:
    observations: list[str] = []
    mood_1 = safe_text(movie_1.get("mood"), "Uncategorized")
    mood_2 = safe_text(movie_2.get("mood"), "Uncategorized")
    genre_1 = safe_text(movie_1.get("genre"), "-")
    genre_2 = safe_text(movie_2.get("genre"), "-")
    tags_1 = movie_1.get("movie_tags", set())
    tags_2 = movie_2.get("movie_tags", set())

    if mood_1 != mood_2:
        observations.append(f"`{label_1}` leans {mood_1.lower()}, while `{label_2}` feels more {mood_2.lower()}.")
    elif genre_1 != genre_2:
        observations.append(f"`{label_1}` and `{label_2}` share a similar mood, but one plays as {genre_1.lower()} and the other as {genre_2.lower()}.")

    intimate_tags = {"tender", "reflective", "character-driven", "melancholic"}
    big_scope_tags = {"epic", "adventurous", "adrenaline", "futuristic", "intense"}
    if (tags_1 & intimate_tags) and (tags_2 & big_scope_tags):
        observations.append(f"`{label_1}` looks more intimate and character-driven, while `{label_2}` is the bigger-scope pick.")
    elif (tags_2 & intimate_tags) and (tags_1 & big_scope_tags):
        observations.append(f"`{label_2}` looks more intimate and character-driven, while `{label_1}` is the bigger-scope pick.")
    else:
        access_1 = describe_accessibility(movie_1)
        access_2 = describe_accessibility(movie_2)
        if access_1 != access_2:
            observations.append(f"`{label_1}` reads as {access_1}, while `{label_2}` feels {access_2}.")

    runtime_1 = movie_1["runtime"] if pd.notna(movie_1["runtime"]) else None
    runtime_2 = movie_2["runtime"] if pd.notna(movie_2["runtime"]) else None
    if runtime_1 and runtime_2 and abs(runtime_1 - runtime_2) >= 30:
        shorter_label = label_1 if runtime_1 < runtime_2 else label_2
        longer_label = label_2 if shorter_label == label_1 else label_1
        observations.append(f"`{shorter_label}` is the lighter time commitment, while `{longer_label}` asks for a longer sit.")

    if not observations:
        imdb_1 = movie_1["imdb_rating"] if pd.notna(movie_1["imdb_rating"]) else None
        imdb_2 = movie_2["imdb_rating"] if pd.notna(movie_2["imdb_rating"]) else None
        if imdb_1 is not None and imdb_2 is not None and imdb_1 != imdb_2:
            higher_label = label_1 if imdb_1 > imdb_2 else label_2
            observations.append(f"Both look fairly close in vibe, but `{higher_label}` comes in with the stronger IMDb rating.")
        else:
            observations.append(f"`{label_1}` and `{label_2}` are close on paper, so the choice mostly comes down to which setup sounds more appealing right now.")

    return " ".join(observations[:2])


movies = load_movie_data(str(DATA_PATH))

for key, value in DEFAULT_KEYS.items():
    st.session_state.setdefault(key, value)
st.session_state.setdefault("compare_selection_order", [])
st.session_state.setdefault("compare_checked_labels", [])

st.title("MovieMatch")
st.write(
    "Discover movies by mood and genre, explore your best matches, and compare two picks side by side before you commit to a watch."
)
st.caption(
    "Use the built-in mood menu for quick browsing, or describe the vibe you want in your own words for a more tailored match."
)
st.divider()

filters_header, reset_col = st.columns([6, 1])
with filters_header:
    st.subheader("1. Find Your Matches")
with reset_col:
    if st.button("Reset filters", use_container_width=True):
        reset_filters()
        st.rerun()

filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    custom_mood = st.text_input(
        "Describe the kind of movie you want",
        key="custom_mood_input",
        placeholder="Examples: sad and beautiful, weird futuristic, dark but funny",
        help="MovieMatch interprets custom phrases into internal mood tags and scores titles by overlap.",
    )
    mood_choice = st.selectbox(
        "Browse by a built-in mood",
        MOOD_OPTIONS,
        key="mood_choice",
        help="Great for quick browsing when you want a broad vibe.",
    )

with filter_col2:
    genre_choice = st.selectbox(
        "Narrow by genre",
        GENRE_OPTIONS,
        key="genre_choice",
        help="Genre works as a simple filter on top of mood-based discovery.",
    )
    title_query = st.text_input(
        "Search by title",
        key="title_search",
        placeholder="Optional: type part of a movie title",
        help="Use this to narrow the list if you already have a few movies in mind.",
    )

results, interpreted_tags = search_movies(
    movies=movies,
    custom_mood_text=custom_mood,
    mood_choice=mood_choice,
    genre_choice=genre_choice,
    title_query=title_query,
)

if interpreted_tags:
    st.info("Interpreted your mood as: " + ", ".join(pretty_tag(tag) for tag in interpreted_tags))
elif custom_mood.strip():
    st.warning(
        "MovieMatch could not confidently interpret that custom mood yet. Try a clearer phrase or use the built-in mood menu."
    )

active_description = []
if interpreted_tags:
    active_description.append("custom mood match")
elif mood_choice != "Any mood":
    active_description.append(mood_choice)
if genre_choice != "Any genre":
    active_description.append(genre_choice)
if title_query.strip():
    active_description.append(f"title search: {title_query.strip()}")

summary_line = f"Showing **{len(results)}** movie(s)"
if active_description:
    summary_line += " for **" + " / ".join(active_description) + "**"
summary_line += "."
st.write(summary_line)

quick_compare_labels: list[str] = []

if results.empty:
    st.warning(
        "No movies matched this combination yet. Try broadening the genre, simplifying the custom mood, or resetting the filters."
    )
    comparison_pool = movies.sort_values(by=["title", "year"], ascending=[True, True])
else:
    top_pick = results.iloc[0]
    st.markdown("#### Top Pick")
    top_left, top_right = st.columns([3, 2], vertical_alignment="top")
    with top_left:
        st.markdown(f"### {top_pick['comparison_label']}")
        st.caption("Best match right now")
        meta_bits = [f"IMDb {display_value(top_pick['imdb_rating'])}"]
        if safe_text(top_pick.get("genre")):
            meta_bits.append(safe_text(top_pick["genre"]))
        if safe_text(top_pick.get("mood")):
            meta_bits.append(safe_text(top_pick["mood"]))
        st.markdown(" | ".join(meta_bits))
    with top_right:
        reason_bits = []
        if interpreted_tags and safe_text(top_pick.get("why_it_fits")):
            reason_bits.append(f"Why it fits: {top_pick['why_it_fits']}")
        if mood_choice != "Any mood":
            reason_bits.append(f"Broad mood: {safe_text(top_pick['mood'])}")
        if not reason_bits:
            reason_bits.append("Strong overall pick based on your current filters.")
        st.markdown("**Match notes**")
        for bit in reason_bits:
            st.write(bit)
    st.caption(build_story_preview(top_pick))
    st.caption("Select up to two titles below. If you check a third, MovieMatch keeps the two most recent choices.")

    discovery_table = build_discovery_table(results, interpreted_tags)
    edited_table = st.data_editor(
        discovery_table,
        width="stretch",
        hide_index=True,
        disabled=[column for column in discovery_table.columns if column != "Compare"],
        column_config={
            "Compare": st.column_config.CheckboxColumn(
                "Compare",
                help="Select up to two titles to send them to the comparison section.",
            )
        },
        key="discovery_compare_table",
        on_change=handle_compare_editor_change,
        args=(discovery_table["Title"].tolist(),),
    )
    quick_compare_labels = st.session_state.get("compare_selection_order", [])
    comparison_pool = results

st.divider()
st.subheader("2. Compare Movies Side by Side")
st.caption(
    "Use the results above to send two titles down here, or choose them manually. The second selector automatically avoids duplicates when possible."
)

first_label, second_label = ensure_comparison_selection(comparison_pool, quick_compare_labels)

if first_label is None or second_label is None:
    st.info("Add more movies to the dataset to unlock side-by-side comparison.")
else:
    compare_col1, compare_col2 = st.columns(2)
    available_labels = comparison_pool["comparison_label"].tolist()

    with compare_col1:
        movie_1_label = st.selectbox(
            "Choose your first movie",
            available_labels,
            index=available_labels.index(first_label),
            key="movie_1",
        )

    second_options = [label for label in available_labels if label != movie_1_label] or [movie_1_label]
    if st.session_state.get("movie_2") not in second_options:
        st.session_state["movie_2"] = second_options[0]

    with compare_col2:
        movie_2_label = st.selectbox(
            "Choose your second movie",
            second_options,
            index=second_options.index(st.session_state["movie_2"]),
            key="movie_2",
        )

    movie_1 = get_movie_by_label(comparison_pool, movie_1_label)
    movie_2 = get_movie_by_label(comparison_pool, movie_2_label)

    preview_col1, preview_col2 = st.columns(2)
    with preview_col1:
        with st.popover(f"Story preview: {movie_1_label}"):
            st.write(build_story_preview(movie_1))
    with preview_col2:
        with st.popover(f"Story preview: {movie_2_label}"):
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
                "Runtime",
                "IMDb rating",
                "Rotten Tomatoes",
            ],
            movie_1_label: [
                display_value(movie_1["year"], 0),
                display_value(movie_1["mood"], 0),
                display_value(movie_1["genre"], 0),
                clean_credit(movie_1["director"]),
                clean_credit(movie_1["top_billed_actors"]),
                clean_credit(movie_1["composer"]),
                clean_credit(movie_1["cinematographer"]),
                format_runtime(movie_1["runtime"]),
                display_value(movie_1["imdb_rating"]),
                display_value(movie_1["rotten_tomatoes"], 0),
            ],
            movie_2_label: [
                display_value(movie_2["year"], 0),
                display_value(movie_2["mood"], 0),
                display_value(movie_2["genre"], 0),
                clean_credit(movie_2["director"]),
                clean_credit(movie_2["top_billed_actors"]),
                clean_credit(movie_2["composer"]),
                clean_credit(movie_2["cinematographer"]),
                format_runtime(movie_2["runtime"]),
                display_value(movie_2["imdb_rating"]),
                display_value(movie_2["rotten_tomatoes"], 0),
            ],
        }
    ).astype(str)
    st.dataframe(comparison_table, width="stretch", hide_index=True)

    st.markdown("**Quick take:** " + build_quick_take(movie_1, movie_2, movie_1_label, movie_2_label))
