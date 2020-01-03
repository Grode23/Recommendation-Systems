import pandas as pd
from collections import defaultdict


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

    counter = 0
    for isbn in isbns:
        counter += 1
        if isbn["count"] < 10:
            for book in books:
                if isbn["isbn"] == book[0]:
                    books.remove(book)
                    break
        if counter == 100:
            break

    return books


def remove_users(ratings, users):
    users_d = defaultdict(int)

    for user in [i[0] for i in ratings]:
        users_d[user] += 1

    users_pass = [{"id": key, "count": value} for key, value in users_d.items()]

    print(len(users_pass))

    counter = 0
    for user_pass in users_pass:
        counter += 1
        if user_pass["count"] < 5:
            for user in users:
                if user_pass["id"] == user[0]:
                    users.remove(user)
                    break
        if counter == 100:
            break

    return users


def main():
    users = get_from_csv("BX-Users.csv")
    books = get_from_csv("BX-Books.csv")
    book_ratings = get_from_csv("BX-Book-Ratings.csv")

    books = remove_books(book_ratings, books)
    users = remove_users(book_ratings, users)

    write_to_csv('books.csv', books)
    write_to_csv('users.csv', users)


main()
