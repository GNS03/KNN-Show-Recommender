import pandas as pd

# import asyncio
# import nest_asyncio
# nest_asyncio.apply()

from request_tv_maze import request_shows, request_search

from sklearn.feature_extraction.text import TfidfVectorizer

# import plotly

def vectorizer_func(df: pd.DataFrame, max_features: int):
    """Function to vectorize genres/columns in the dataframe"""

    vectorizer = TfidfVectorizer(max_features=max_features, stop_words='english')  # stop_words='english'

    X = vectorizer.fit_transform(df['features'])
    
    return X.toarray(), vectorizer.get_feature_names_out()


def rec_show(query: str, media_type: str, pages: int = 10, limit: int = 10, extended_level: str = "full", max_features: int = 50, n_neighbors: int = 10):

    shows = request_shows(pages = pages, limit = limit, extended_level=extended_level) # pages X limit

    shows_df = pd.json_normalize(shows)

    new_show = request_search(query, media_type)

    print(f"Found {new_show.get("title")}")

    query = new_show["title"].lower()

    new_show_df = pd.json_normalize(new_show)

    if new_show["title"] not in shows_df.title.values:
        shows_df = pd.concat([shows_df, new_show_df], ignore_index=True, axis=0)

    # Combine features while handling NaN values
    print("Creating features...")
    features = (
            shows_df["type"].fillna("")
            + " "
            + shows_df["language"].fillna("")
            + " "
            + shows_df["summary"].fillna("")
    )

    # Process genres column
    genres_unpacked = shows_df["genres"].apply(
        lambda x: " ".join(x).lower() if isinstance(x, list) else x.lower() if isinstance(x, str) else ""
    )

    shows_df["genres"] = genres_unpacked

    # Combine genres with other features
    features += " " + genres_unpacked

    # print(features)

    shows_df["features"] = features

    vectorized_features, feature_names = vectorizer_func(shows_df, max_features)

    vectorized_df = pd.DataFrame(vectorized_features, columns = feature_names)

    shows_df_concat = pd.concat([shows_df, vectorized_df], axis=1)

    from sklearn.neighbors import NearestNeighbors

    knn_df = shows_df_concat.iloc[:, 6:]

    print("Generating neighbors...")
    rec = NearestNeighbors(metric = 'cosine')
    rec.fit(knn_df)

    distances, indices = rec.kneighbors(knn_df, n_neighbors) # Number of recommendations

    for idx, show_index in enumerate(indices):

        if shows_df.iloc[idx]["title"].lower() != query:  # Use == for comparison
            continue

        print(f"Similar items to show, {shows_df_concat.iloc[idx]['title']}:")
        print(str(shows_df_concat.iloc[idx]["genres"]))
        print()
        for neighbor_idx, neighbor_distance in zip(show_index[1:], distances[idx][1:]):
            if shows_df_concat.iloc[neighbor_idx]['title'] != shows_df_concat.iloc[idx]['title']:
                print(f"{shows_df_concat.iloc[neighbor_idx]['title']}: {str(shows_df_concat.iloc[neighbor_idx]['genres'])} (Distance: {neighbor_distance:.3f})")
        print()