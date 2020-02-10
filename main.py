import os  # For directory creation
import sys  # For argv
from operator import itemgetter
from pathlib import Path  # Path to save results to

import pandas as pd  # For CSV
from collections import defaultdict, OrderedDict  # For removal of unnecessary items on the lists
from random import randint  # For random integer


def get_from_csv(file_name):
    # Read the CSV into a pandas data frame (df)
    # Encoding to ISO-8859-1 because of the non-ASCII characters
    # Some lines contain ';' as a character and for that reason, I get some errors. error_bad_lines handles those lines
    df = pd.read_csv(file_name, delimiter=';', encoding="ISO-8859-1", error_bad_lines=False, dtype='unicode')

    # Return a list with the values of the CSV file
    return [list(x) for x in df.values]


def write_to_csv(file_name, my_list):
    df = pd.DataFrame(my_list)

    # saving the dataframe
    df.to_csv(file_name, index=False, sep=';', encoding='ISO-8859-1')


# Remove unnecessary books from the CSV
def remove_books(ratings, books):

    # Key is ISBN and value the amount of times it exists
    isbn_d = defaultdict(int)

    for isbn in [i[1] for i in ratings]:
        isbn_d[isbn] += 1

    isbns = [{"isbn": key, "count": value} for key, value in isbn_d.items()]

    new_books = []

    for isbn in isbns:
        # If it has at least 10 ratings, add it
        if isbn["count"] >= 10:
            for book in books:
                if isbn["isbn"] == book[0]:
                    new_books.append(book)
                    break

    return new_books


# Remove unnecessary users from the CSV
def remove_users(ratings, users):

    # Key is id and value the amount of times they exist
    users_d = defaultdict(int)

    for user in [i[0] for i in ratings]:
        users_d[user] += 1

    users_pass = [{"id": key, "count": value} for key, value in users_d.items()]

    new_users = []

    for user_pass in users_pass:
        # If they have at least 5 ratings, add them
        if user_pass["count"] >= 5:
            for user in users:
                if user_pass["id"] == user[0]:
                    new_users.append(user)
                    break

    return new_users


# Remove unnecessary ratings from CSV
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
    # A dictionary with ISBN as key and a list of keywords as value
    keywords = {}

    for book in books:
        isbn = book[0]
        title = book[1]

        # Split title into words
        keywords[isbn] = title.split()

        # Remove duplicates
        keywords[isbn] = list(OrderedDict.fromkeys(keywords[isbn]))

        temp = []
        for keyword in keywords[isbn]:

            # Remove too short words
            # Not the best way of doing the stopwords
            # But it's definitely the quickest/easiest
            if len(keyword) > 2:

                # Remove words with numbers since they probably represent a false statement about liking of a user
                valid = True
                for char in keyword:
                    # If any character of a word is a digit, don't add it to the keywords
                    if char.isdigit():
                        valid = False
                        break
                if valid:
                    temp.append(keyword.lower())  # When append, transform to lowercase

        # I cannot manipulate keywords[isbn] because I iterate through it, so I add a temp with the correct values
        # And then I add it to the keywords list
        keywords[isbn] = temp

        temp_keywords = []

        # Remove non character letter such as (, ), /, \ etc
        for keyword in keywords[isbn]:
            temp_keyword = keyword
            second_temp_keyword = None
            for char in keyword:

                if char.isalpha() is False:

                    # Index of the next char
                    next_index = keyword.index(char) + 1

                    # If it's not the last or the first index and the next character is a letter
                    if len(keyword) > next_index != 1 and keyword[next_index].isalpha() is True:

                        # Replace character with space and keep these words seperate
                        both_temp_keywords = temp_keyword.replace(char, " ").split()

                        # If the first word isn't too short, add it to temp_keyword
                        if len(both_temp_keywords[0]) > 2:
                            temp_keyword = both_temp_keywords[0]

                        # if a second word really exists
                        if len(both_temp_keywords) == 2:
                            # And it's not too short, add it to second_temp_keyword
                            if len(both_temp_keywords[1]) > 2:
                                second_temp_keyword = both_temp_keywords[1]

                    else:
                        temp_keyword = temp_keyword.replace(char, "")

            temp_keywords.append(temp_keyword)

            # Add second_temp_keyword is it exists
            if second_temp_keyword is not None:
                temp_keywords.append(second_temp_keyword)

        # Add every keyword of the current book
        keywords[isbn] = temp_keywords

    return keywords


# Get the 3 top rated books for each user
def get_favourites(book_ratings, user_id, books):

    favourites = []

    # Iterate through every rating to find ratings from this specific user
    for rating in book_ratings:

        # If the rating is from this user
        if user_id == rating[0]:

            # If the book exists
            if rating[1] in [i[0] for i in books]:

                to_be_inserted = [rating[1], rating[2]]

                # Check if the user already has 3 favourites or not
                if len(favourites) < 3:

                    # If he doesn't, insert this one
                    favourites.append(to_be_inserted)
                else:

                    # if he does, go through these three
                    for favourite in favourites:

                        # And check if the current rating is higher than a previous one
                        if rating[2] > favourite[1]:
                            favourites.remove(favourite)
                            favourites.append(to_be_inserted)
                            break

    return favourites


# Favourite authors, years of publication and keywords from titles
def get_preferences(favourites, books, keywords):

    authors = []
    keywords_in_titles = []
    year_of_publications = []

    for book in books:

        book_isbn = book[0]
        book_author = book[2]
        book_year = book[3]

        for user_favourite in favourites:

            if user_favourite[0] == book_isbn:

                # Add author
                authors.append(book_author)

                # Add year of publication
                year_of_publications.append(book_year)

                # Add keywords from titles
                # Need to move keywords from each favourite book into one list, not three separated
                for keyword in keywords[book_isbn]:
                    keywords_in_titles.append(keyword)

    preferences = [authors, keywords_in_titles, year_of_publications]

    return preferences


def get_random_users(users, amount=5):
    random_users = []

    for i in range(amount):
        choices = randint(0, len(users))
        random_users.append(users[choices])

    return random_users


# Both Jaccard and Dice-coefficient are running through this
def uniformity(books, users_preferences, keywords, type_of_uniformity):

    # Add the right values
    if type_of_uniformity is "jaccard":
        author_value = 0.4
        keywords_value = 0.2
        year_value = 0.4
    else:
        author_value = 0.3
        keywords_value = 0.5
        year_value = 0.2

    # User's results for every book
    user_results = []

    preferences = users_preferences

    # Separate preferences for better understanding of the code
    user_years = preferences[2]
    user_keywords = preferences[1]
    user_authors = preferences[0]

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
        if type_of_uniformity is "jaccard":
            user_result = jaccard(user_result, user_keywords, keywords_from_book, keywords_value)
        else:
            user_result = dice(user_result, user_keywords, keywords_from_book, keywords_value)

        # Check year of publication
        for user_year in user_years:
            tmp = 1 - (abs(int(year) - int(user_year)) / 2005)
            curr_result = 0
            if tmp > curr_result:
                curr_result = tmp

        user_result += curr_result * year_value

        user_results.append([isbn, user_result])

    return user_results


def jaccard(result, user_keywords, keywords_from_book, keywords_value):

    common_keywords = 0

    # Keywords from one set
    keywords_from_both = keywords_from_book.copy()

    # Rest of the keywords
    for keyword in user_keywords:
        if keyword not in keywords_from_both:
            keywords_from_both.append(keyword)

    length_both_sets = len(keywords_from_both)

    # If I removed every keyword (for example "2001" because I remove numbers)
    if len(keywords_from_book) > 0:
        for keyword_from_book in keywords_from_book:
            if keyword_from_book in user_keywords:
                common_keywords += 1

        result += (common_keywords / length_both_sets) * keywords_value

    return result


def dice(result, user_keywords, keywords_from_book, keywords_value):

    common_keywords = 0

    # If I removed every keyword (for example "2001" because I remove numbers)
    if len(keywords_from_book) > 0:
        for keyword_from_book in keywords_from_book:
            if keyword_from_book in user_keywords:
                common_keywords += 1

        total_length = len(keywords_from_book) + len(user_keywords)

        result += (2 * common_keywords / total_length) * keywords_value

    return result


def suggest_books(books, results):

    suggested_results = []
    suggested_books = []

    suggested_counter = 0

    for book in books:
        for result in results:
            # If the current result is about this book
            if result[0] == book[0]:
                curr_result = result[1]

                # If the book is already read, don't mind about it
                if curr_result == 1.0:
                    continue

                # If this user has 10 suggestions
                elif suggested_counter == 10:
                    # Check if any of the suggestions has lower result value than the current
                    for suggested_book in suggested_results:
                        if curr_result > suggested_book[1]:
                            # suggested_book = result
                            index = suggested_results.index(suggested_book)
                            suggested_results[index] = result
                            suggested_books[index] = book
                            break
                else:
                    suggested_results.append(result)
                    suggested_books.append(book)
                    suggested_counter += 1

    return suggested_books, suggested_results


# Write suggestions to text files
# 2 files for each user
# One file for Jaccard and one file for Dice coefficient
def write_suggestions(user_index, suggestions, result_type):

    # Create directory named results if it does not exist
    if not os.path.exists("results/"):
        os.makedirs("results/")

    # Name of the file is the index of user and the type of the uniformity
    # Example: user-0-jaccard.txt
    file_name = "user-" + user_index + "-" + result_type + ".txt"
    data_folder = Path("results/")
    file_name = data_folder / file_name

    with open(file_name, 'w') as f:
        for suggestion in suggestions:
            f.write("ISBN: %s \t with title: %s\nAuthor is: %s and year is %s\n" % (
                suggestion[0], suggestion[1], suggestion[2], suggestion[3]))


def overlap(jaccard_results, dice_results):

    for i in range(10):
        books_from_jaccard = []
        for j in range(i + 1):
            books_from_jaccard.append(jaccard_results[j][0])

        fraction = 0
        for j in range(i + 1):
            if dice_results[j][0] in books_from_jaccard:
                fraction += 1

        fraction = fraction / (i + 1)

    print(fraction)

    return fraction


# This list isn't sorted because I have to check two variables: Amount of times and result
def sort_golden(goldens, most_times=2):

    sorted_golden = []

    # First of all, add result that appears many times
    for times in range(most_times, 0, -1):
        temp_sorted = []
        for golden in goldens:

            # Sort all items of each specific time
            if golden[1] == times:
                temp_sorted.append(golden)

        temp_sorted = sorted(temp_sorted, key=itemgetter(2), reverse=True)

        # Add them all together
        for temp in temp_sorted:
            sorted_golden.append(temp)

    return sorted_golden


def get_golden(jaccard_results, dice_results):

    goldens = []
    books = {}

    for jaccard_result in jaccard_results:

        curr_isbn = jaccard_result[0]
        times = 1

        books[curr_isbn] = []

        # In how many favourite lists a book exists
        if curr_isbn in [dice_result[0] for dice_result in dice_results]:
            times += 1

        for dice_result in dice_results:

            dice_to_be_removed = None
            if dice_result[0] == curr_isbn:
                curr_result = dice_result[1]
                break

            if times == 1:
                dice_to_be_removed = dice_result
                goldens.append([dice_result[0], times, dice_result[1]])
                break

        # Remove it if this book exists in Jaccard too
        if dice_to_be_removed is not None:
            dice_results.remove(dice_to_be_removed)

        average_result = (curr_result + jaccard_result[1]) / 2

        goldens.append([curr_isbn, times, average_result])

    return sort_golden(goldens)


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
    # Experiment 1

    # Keep three random users, not everyone
    users = get_random_users(users)

    # Initialization of every dict
    users_favourites = {}
    preferences = {}
    results_jaccard, results_dice = {}, {}
    suggested_books_jaccard, suggested_books_dice = {}, {}
    suggested_results_jaccard, suggested_results_dice = {}, {}
    golden_standard = {}

    # Repeat the whole process for every user
    for user in users:

        curr_id = user[0]

        users_favourites[curr_id] = []
        preferences[curr_id] = []
        results_dice[curr_id], results_jaccard[curr_id] = [], []

        # Find the 3 top rated books for every user
        users_favourites[curr_id] = get_favourites(book_ratings, curr_id, books)
        print("Found favourite books for the random users")

        # Get Data from favourite books for the random users
        preferences[curr_id] = get_preferences(users_favourites[curr_id], books, keywords)
        print("Preferences of random users are created")

        results_jaccard[curr_id] = uniformity(books, preferences[curr_id], keywords, "jaccard")
        print("Jaccard is done")

        results_dice[curr_id] = uniformity(books, preferences[curr_id], keywords, "dice")
        print("Dice coefficient is done")

        suggested_book_jaccard, suggested_result_jaccard = suggest_books(books, results_jaccard[curr_id])
        suggested_books_jaccard[curr_id] = suggested_book_jaccard
        suggested_results_jaccard[curr_id] = suggested_result_jaccard
        print("Book suggestions for Jaccard has being done")

        suggested_book_dice, suggested_result_dice = suggest_books(books, results_dice[curr_id])
        suggested_books_dice[curr_id] = suggested_book_dice
        suggested_results_dice[curr_id] = suggested_result_dice
        print("Book suggestions for dice coefficient has being done")

        write_suggestions(str(users.index(user)), suggested_books_jaccard[curr_id], "jaccard")
        write_suggestions(str(users.index(user)), suggested_books_dice[curr_id], "dice")

        # Experiment 2

        fractions = overlap(suggested_results_jaccard[curr_id], suggested_results_dice[curr_id])
        print("Overlapping is done")

        # Experiment 3
        golden_standard[curr_id] = get_golden(suggested_results_jaccard[curr_id], suggested_results_dice[curr_id].copy())

        overlap(suggested_results_jaccard[curr_id], golden_standard[curr_id])
        print("Overlap with golden and jaccard")
        overlap(suggested_results_dice[curr_id], golden_standard[curr_id])
        print("Overlap with golden and dice")

        print("User", str(users.index(user)), "is done")
        print("____________________________________________")


main()
