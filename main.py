import sys

import pandas as pd  # For CSV
from collections import defaultdict, OrderedDict  # For removal of unnecessary items on the lists
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
        isbn = book[0]
        title = book[1]

        keywords[isbn] = []
        keywords[isbn] = title.split()

        # Remove duplicates
        keywords[isbn] = list(OrderedDict.fromkeys(keywords[isbn]))

        temp = []
        for keyword in keywords[isbn]:

            # Remove too short words
            if len(keyword) > 2:

                # Remove words with numbers since they probably represent a false statement about liking of a user
                valid = True
                for char in keyword:
                    if char.isdigit():
                        valid = False
                        break
                if valid:
                    temp.append(keyword.lower())  # When append, transform to lowercase

        keywords[isbn] = temp

        # Remove non character letter such as (, ), /, \ etc

        temp_keywords = []

        for keyword in keywords[isbn]:
            temp_keyword = keyword
            for char in keyword:

                if char.isalpha() is False:
                    next_index = keyword.index(char) + 1
                    if len(keyword) != next_index and keyword[next_index].isalpha is False:
                        temp_keyword = temp_keyword.replace(char, " ")
                    else:
                        temp_keyword = temp_keyword.replace(char, "")

            temp_keywords.append(temp_keyword)

        keywords[isbn] = temp_keywords

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
    users_preferences = {}

    for user_id in favourites:
        users_preferences[user_id] = []
        author = []
        keywords_in_title = []
        year_of_publication = []

        for book in books:

            book_isbn = book[0]
            book_author = book[2]
            book_year = book[3]

            for user_favourite in favourites[user_id]:
                if user_favourite[0] == book_isbn:

                    # Add author
                    author.append(book_author)

                    # Add year of publication
                    year_of_publication.append(book_year)

                    # Add keywords from titles
                    # Need to move keywords from each favourite book into one list, not three separated
                    for keyword in keywords[book_isbn]:
                        keywords_in_title.append(keyword)

        preferences = [author, keywords_in_title, year_of_publication]
        users_preferences[user_id] = preferences

    return users_preferences


def get_random_users(users):
    random_users = []

    for i in range(5):
        choices = randint(0, len(users))
        random_users.append(users[choices])

    return random_users


def jaccard(users, books, users_preferences, keywords, author_value=0.4, keywords_value=0.2, year_value=0.4):

    results = {}

    for user in users:

        user_id = user[0]

        # Initialization of result of every user on every book
        results[user_id] = []

        # User's results for every book
        user_results = []

        preferences = users_preferences[user_id]

        # Separate preferences for better understanding of the code
        user_years = preferences.pop()
        user_keywords = preferences.pop()
        user_authors = preferences.pop()

        for book in books:

            # User result is equal to 0 for every book before any calculation
            user_result = 0

            isbn = book[0]

            author = book[2]
            year = book[3]
            keywords_from_book = keywords[isbn]

            # Check author

            if author in user_authors:
                user_result += author_value

            # Check keywords

            common_keywords = 0

            # If I removed every keyword (for example "2001" because I remove numbers)
            if len(keywords_from_book) > 0:
                for keyword_from_book in keywords_from_book:
                    if keyword_from_book in user_keywords:
                        common_keywords += 1

                user_result += (common_keywords / len(keywords_from_book)) * keywords_value

            # Check year of publication

            for user_year in user_years:
                tmp = 1 - (abs(int(year) - int(user_year)) / 2005)
                curr_result = 0
                if tmp > curr_result:
                    curr_result = tmp

            user_result += curr_result * year_value

            # if user_result > 0.8:
            #     print("ISBN: ", isbn, " with ", user_result)

            user_results.append([isbn, user_result])

        results[user_id] = user_results

    return results


def suggest_books(users, books, results):
    print()


def main():
    # Pre-treatment 1

    if len(sys.argv) == 1:
        users_file = "users2.csv"
        books_file = "books2.csv"
        ratings_file = "ratings.csv"

        users = get_from_csv(users_file)
        books = get_from_csv(books_file)
        book_ratings = get_from_csv(ratings_file)
    elif len(sys.argv) == 2 and sys.argv[1] == "start":

        # I repeat it, because when ratings are removed, some users, still have less than 5 ratings
        # So I need to remove even more users and even more books
        # Eventually I have the right amount of users, books and ratings
        # But just in case, I still check if the book and user of any rating exists furthermore on the project
        for i in range(3):
            users_file = "BX-Users.csv"
            books_file = "BX-Books.csv"
            ratings_file = "BX-Book-Ratings.csv"

            users = get_from_csv(users_file)
            books = get_from_csv(books_file)
            book_ratings = get_from_csv(ratings_file)

            books = remove_books(book_ratings, books)
            print("Books were removed.")
            write_to_csv(books_file, books)
            print("Books are saved")

            users = remove_users(book_ratings, users)
            print("Users were removed.")
            write_to_csv(users_file, users)
            print("Users are saved")

            book_ratings = remove_ratings(book_ratings, books, users)
            print("Ratings were removed")
            write_to_csv(ratings_file, book_ratings)
            print("Ratings were saved")
    else:
        print("Wrong argument(s)")
        exit(0)

    print("Data is taken from the CSV files")

    # Pre-treatment 2

    keywords = get_keywords_from_title(books)
    print("Found keywords from every book title")

    # Recommendation system

    # Keep three random users, not everyone
    users = get_random_users(users)

    # Find the 3 top rated books for every user
    users_favourites = get_favourites(book_ratings, users, books)
    print("Found favourite books for the random users")

    # Get Data from favourite books for the random users
    preferences = get_preferences(users_favourites, books, keywords)
    print("Preferences of random users are created")

    results = jaccard(users, books, preferences, keywords)

    suggest_books(users, books, results)
    print("Books has been suggested")


main()