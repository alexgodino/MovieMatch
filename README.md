# MovieMatch

**Student Name:** `Alex Godino`

MovieMatch is a Streamlit movie discovery app that helps users find films by mood and genre, then compare two choices side by side. The app is designed as a polished final class project: it gives users a simple browse path, supports more descriptive custom mood input, and turns a large movie dataset into recommendations that feel curated instead of random.

## Target Users

MovieMatch is built for general movie watchers who:
- want a recommendation based on how they feel
- want to narrow choices by genre
- want a quick way to compare two movies before deciding what to watch

## Final Features

- Clear app title and short instructions
- Multiple input widgets: custom mood text, mood dropdown, genre filter, title search, and comparison selectors
- Interactive movie discovery with custom mood interpretation
- Layered mood system using built-in moods, internal tags, synonym mapping, and fuzzy matching backup
- Scored recommendations instead of strict all-or-nothing matching
- Hidden curation logic that can use `your_rating` when available without showing it in the interface
- Top Pick section that highlights the strongest current match
- Interactive results table with compare checkboxes
- Side-by-side comparison view for two selected movies
- Graceful handling of missing optional columns such as `plot_blurb` and `your_rating`
- Cached CSV loading for smoother performance
- Deployment-ready structure using Streamlit, pandas, and the Python standard library only

## How To Use MovieMatch

1. Open the app.
2. Describe the kind of movie you want in your own words, or choose a built-in mood.
3. Optionally narrow the list by genre or title search.
4. Review the Top Pick and filtered results.
5. Select up to two movies to compare side by side.
6. Use the reset button any time to start a new search.

## Files In This Project

- `app.py` - main Streamlit application
- `movies.csv` - movie dataset used by the app
- `README.md` - project overview and submission notes
- `Requirements.txt` - minimal project dependencies

## Run Locally

1. Install dependencies:
   `python -m pip install -r Requirements.txt`
2. Start the Streamlit app:
   `python -m streamlit run app.py`

## Submission Links

- **Deployed App:** `[Add Streamlit app link here]`
- **GitHub Repository:** `[Add GitHub repo link here]`

## Project Summary

MovieMatch goes beyond a toy example by combining recommendation logic, filtering, hidden ranking signals, and side-by-side comparison in one app. The final version focuses on usability, clean layout, readable code, and a smooth interactive flow suitable for a final class submission.
