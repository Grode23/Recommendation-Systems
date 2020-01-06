import pandas as pd  # For CSV
from collections import defaultdict  # For removal of unnecessary items on the lists
from random import randint  # For random integer


def get_from_csv(file_name):
    # Read the CSV into a pandas data frame (df)
    #   With a df you can do many things
    #   most important: visualize data with Seaborn
    df = pd.read_csv(file_name, delimiter=';', encoding="ISO-8859-1", error_bad_lines=False, dtype='unicode')

    # Or export it in many ways, e.g. a list of tuples
    return [list(x) for x in df.values]

    # or export it as a list of dicts
    # dicts = df.to_dict().values()


def write_to_csv(file_name, my_list):
    df = pd.DataFrame(my_list)

    # saving the dataframe
    df.to_csv(file_name, index=False, sep=';', encoding='ISO-8859-1')


def remove_books(ratings, books):
    isbn_d = defaultdict(int)

    for isbn in [i[1] for i in ratings]:
        isbn_d[isbn] += 1

    isbns = [{"isbn": key, "count": value} for key, value in isbn_d.items()]

    new_books = []

    for isbn in isbns:
        if isbn["count"] >= 10:
            for book in books:
                if isbn["isbn"] == book[0]:
                    new_books.append(book)
                    break

    return new_books


def remove_users(ratings, users):
    users_d = defaultdict(int)

    for user in [i[0] for i in ratings]:
        users_d[user] += 1

    users_pass = [{"id": key, "count": value} for key, value in users_d.items()]

    new_users = []

    for user_pass in users_pass:
        if user_pass["count"] >= 5:
            for user in users:
                if user_pass["id"] == user[0]:
                    new_users.append(user)
                    break

    return new_users


def remove_ratings(ratings, books, users):
    new_ratings = []

    # For every rating
    for rating in ratings:
        # If user exists and book exist too
        if rating[0] in [i[0] for i in users] and rating[1] in [i[0] for i in books]:
            # Keep that rating
            new_ratings.append(rating)

    return new_ratings


def get_keywords_from_title(books):
    keywords = {}

    for book in books:
        keywords[book[0]] = []
        keywords[book[0]].append(book[1].split())

    return keywords


def get_favourites(book_ratings, users, books):
    # Dictionary with users' id (key) and their favourite books' ISBN and personal rating (value of list)
    favourites = {}

    # Iterate through users
    for user in users:

        user_id = user[0]

        # Item in dictionary for every user
        favourites[user_id] = []

        # Iterate through every rating to find ratings from this specific user
        for rating in book_ratings:

            # If the rating is from this user
            if user_id == rating[0]:

                if rating[1] in [i[0] for i in books]:

                    to_be_inserted = [rating[1], rating[2]]

                    # Check if the user already has 3 favourites or not
                    if len(favourites[user_id]) < 3:

                        # If he doesn't, insert this one
                        favourites[user_id].append(to_be_inserted)
                    else:

                        # if he does, go through these three
                        for favourite in favourites[user_id]:

                            # And check if the current rating is higher than a previous one
                            if rating[2] > favourite[1]:
                                favourites[user_id].remove(favourite)
                                favourites[user_id].append(to_be_inserted)
                                break

    return favourites


def get_preferences(favourites, books, keywords):

    for user_id in favourites:
        print(favourites[user_id])
        author = []
        keywords_in_title = []
        year_of_publication = []

        for book in books:
            for user_favourite in favourites[user_id]:
                if user_favourite[0] == book[0]:
                    print(user_favourite)
                    # Add author
                    author.append(book[2])

                    # Add year of publication
                    year_of_publication.append(book[3])

                    # Add keywords from titles
                    keywords_in_title.append(keywords[book[0]])


def get_random_users(users):
    random_users = []

    for i in range(5):
        choices = randint(0, len(users))
        random_users.append(users[choices])

    return random_users


def main():

    users_file = "users2.csv"
    books_file = "books2.csv"
    ratings_file = "ratings.csv"

    # Pre-treatment 1

    # I repeat it, because when ratings are removed, some users, still have less than 5 ratings
    # So I need to remove even more users and even more books
    # Eventually I have the right amount of users, books and ratings
    # But just in case, I still check if the book and user of any rating exists furthermore on the project
    # for i in range(3):
    #     users = get_from_csv(users_file)
    #     books = get_from_csv(books_file)
    #     book_ratings = get_from_csv(ratings_file)
    #
    #     books = remove_books(book_ratings, books)
    #     print("Books were removed.")
    #     write_to_csv(books_file, books)
    #     print("Books are saved")
    #
    #     users = remove_users(book_ratings, users)
    #     print("Users were removed.")
    #     write_to_csv(users_file, users)
    #     print("Users are saved")
    #
    #     book_ratings = remove_ratings(book_ratings,books, users)
    #     print("Ratings were removed")
    #     write_to_csv(ratings_file, book_ratings)
    #     print("Ratings were saved")

    users = get_from_csv(users_file)
    books = get_from_csv(books_file)
    book_ratings = get_from_csv(ratings_file)

    print("Done with pre-treatment #1")

    # Pre-treatment 2

    keywords = get_keywords_from_title(books)
    print("Found keywords from every book title")

    # Recommendation system

    # Keep three random users, not everyone
    users = get_random_users(users)

    # Find the 3 top rated books for every user
    users_favourites = get_favourites(book_ratings, users, books)
    print("Found favourite books for the random users")

    # Get Data from top rated books for the random users
    get_preferences(users_favourites, books, keywords)


main()
