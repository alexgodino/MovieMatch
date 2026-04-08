# MovieMatch

MovieMatch is a Streamlit app for discovering movies by mood and genre, then comparing matching titles side by side. The current version uses a large movie database, custom mood input, interactive filtering, and a comparison view that helps users explore films by tone, genre, plot, and key movie details.

## Current Features

- App title and short description
- Larger movie database stored in a separate CSV file for easier growth
- Hidden taste-profile ranking based on imported Letterboxd history
- Custom mood input with broader mood-tag matching
- Mood and genre filtering to narrow movie options
- Default browse view with Any mood and Any genre showing the full movie list
- Interactive result table that connects browsing to comparison
- Dynamic comparison table that updates based on user choices
- Movie details including release year, director, cast, composer, cinematographer, runtime, IMDb, Rotten Tomatoes, and plot summaries

## Planned Features

- Make the comparison flow smoother and less finicky
- Improve mood tagging so results feel more specific and accurate
- Expand and refine the quick-take recommendation summary
- Continue polishing imported movie metadata where needed
- Additional filters such as release year
- Charts or visualizations for ratings and trends
- User ratings, favorites, or watchlist features

## Running the App

1. Install the project dependency:
   `python -m pip install -r Requirements.txt`
2. Start the Streamlit app:
   `python -m streamlit run app.py`

## Assignment 2 Progress Summary

### Features Added

- Added a short description explaining the app's purpose
- Expanded the movie dataset substantially
- Added mood and genre filtering for discovery
- Added custom mood input and richer mood-tag matching
- Connected the comparison section to the filtered movie results
- Added interactive comparison selection from the result table
- Added a dynamic comparison table showing key movie attributes
- Added real plot summaries for movie previews
- Cleaned up movie metadata using imported Letterboxd history and OMDb data
- Improved the overall layout and readability of the app

### Remaining Work

- Refine mood categorization so typed moods produce stronger matches
- Smooth out the comparison tool interaction
- Improve the quick-take summary and recommendation logic
- Add more advanced visualizations or recommendation insights
- Continue general UI cleanup and polish

### Challenges Encountered

- Expanding the movie data while keeping the app manageable
- Making discovery and comparison feel like one connected flow
- Cleaning imported movie metadata so the app stays consistent
- Designing a mood system that feels flexible without becoming confusing
