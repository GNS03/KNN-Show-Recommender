from knn import rec_show

if __name__ == "__main__":

    print("Starting")
    show = input("Type the name of the show you want to get recommendations for: ")
    media_type = "shows"
    max_features = int(input("Type the maximum number of features you want: "))
    n_neighbors = int(input("Type the number of recommendations you want: "))
    print()

    rec_show(query=show, media_type=media_type, pages=20, max_features=max_features, n_neighbors=n_neighbors)
    input("Press Enter to Exit")