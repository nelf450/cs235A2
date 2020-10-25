import csv
import os
from datetime import date, datetime
from typing import List
import random
import math
from bisect import bisect, bisect_left, insort_left

from werkzeug.security import generate_password_hash

from movie.adapters.repository import AbstractRepository, RepositoryException
from movie.domain.model import Article, Tag, User, Comment, make_tag_association, make_comment
from imdb import IMDb


class MemoryRepository(AbstractRepository):
    # Articles ordered by date, not id. id is assumed unique.

    def __init__(self):
        self._articles = list()
        self._articles_index = dict()
        self._tags = list()
        self._actors = list()
        self._users = list()
        self._comments = list()

    def add_user(self, user: User):
        self._users.append(user)

    def get_user(self, username) -> User:
        return next((user for user in self._users if user.username == username), None)

    def add_article(self, article: Article):
        insort_left(self._articles, article)
        self._articles_index[article.id] = article

    def get_article(self, id: int) -> Article:
        article = None

        try:
            article = self._articles_index[id]
        except KeyError:
            pass  # Ignore exception and return None.

        return article

    def get_articles_by_date(self, target_date: date) -> List[Article]:
        target_article = Article(
            date=target_date,
            title=None,
            first_para=None,
            hyperlink=None,
            image_hyperlink=None
        )
        matching_articles = list()

        try:
            index = self.article_index(target_article)
            for article in self._articles[index:None]:
                if article.date == target_date:
                    matching_articles.append(article)
                else:
                    break
        except ValueError:
            # No articles for specified date. Simply return an empty list.
            pass

        return matching_articles

    def get_number_of_articles(self):
        return len(self._articles)

    def get_first_article(self):
        article = None

        if len(self._articles) > 0:
            article = self._articles[0]
        return article

    def get_last_article(self):
        article = None

        if len(self._articles) > 0:
            article = self._articles[-1]
        return article

    def get_articles_by_id(self, id_list):
        # Strip out any ids in id_list that don't represent Article ids in the repository.
        existing_ids = [id for id in id_list if id in self._articles_index]

        # Fetch the Articles.
        articles = [self._articles_index[id] for id in existing_ids]
        return articles

    def get_article_ids_for_tag(self, tag_name: str):
        # Linear search, to find the first occurrence of a Tag with the name tag_name.
        tag = next((tag for tag in self._tags if tag.tag_name == tag_name), None)

        # Retrieve the ids of articles associated with the Tag.
        if tag is not None:
            article_ids = [article.id for article in tag.tagged_articles]
        else:
            # No Tag with name tag_name, so return an empty list.
            article_ids = list()

        return article_ids

    def get_date_of_previous_article(self, article: Article):
        previous_date = None

        try:
            index = self.article_index(article)
            for stored_article in reversed(self._articles[0:index]):
                if stored_article.date < article.date:
                    previous_date = stored_article.date
                    break
        except ValueError:
            # No earlier articles, so return None.
            pass

        return previous_date

    def get_date_of_next_article(self, article: Article):
        next_date = None

        try:
            index = self.article_index(article)
            for stored_article in self._articles[index + 1:len(self._articles)]:
                if stored_article.date > article.date:
                    next_date = stored_article.date
                    break
        except ValueError:
            # No subsequent articles, so return None.
            pass

        return next_date

    def add_tag(self, tag: Tag):
        self._tags.append(tag)

    def get_tags(self) -> List[Tag]:
        return self._tags

    def add_comment(self, comment: Comment):
        super().add_comment(comment)
        self._comments.append(comment)

    def get_comments(self):
        return self._comments

    # Helper method to return article index.
    def article_index(self, article: Article):
        index = bisect_left(self._articles, article)
        if index != len(self._articles) and self._articles[index].date == article.date:
            return index
        raise ValueError


def read_csv_file(filename: str):
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        # Read first line of the the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row


def load_articles_and_tags(data_path: str, repo: MemoryRepository):
    tags = dict()
    count_days = 0
    count_months = 0

    for data_row in read_csv_file(os.path.join(data_path, 'Data1000Movies.csv')):

        article_key = int(data_row[0])
        article_tags = data_row[2].split(",")

        # Add any new tags; associate the current article with tags.
        for tag in article_tags:
            if tag not in tags.keys():
                tags[tag] = list()
            tags[tag].append(article_key)

        if count_days == 27:
            count_days = 0
        if count_months == 11:
            count_months = 0

        release_date = str(int(data_row[6]) + 1)
        months = []
        for i in range(1, 13):
            if i < 10:
                months.append("0" + str(i))
            if i >= 10:
                months.append(str(i))
        count_months += 1

        days = []
        for i in range(1, 29):
            if i < 10:
                days.append("0" + str(i))
            if i >= 10:
                days.append(str(i))
        count_days += 1

        release_date = release_date + '-' + months[count_months] + '-' + days[count_days]

        """
        ia = IMDb()
        actor_string = data_row[5]
        split_actor_string = actor_string[0].split(",")
        
        if len(split_actor_string) >= 2:
            acting_one = split_actor_string[0].strip()
            acting_two = split_actor_string[1].strip()

            acting_one_search = ia.search_person(acting_one)
            acting_one_id = acting_one_search[0].personID
            acting_one = ia.get_person(acting_one_id)

            acting_two_search = ia.search_person(acting_two)
            acting_two_id = acting_two_search[0].personID
            acting_two = ia.get_person(acting_two_id)
        
        movie_search = ia.search_movie(data_row[1])
        movie_search_id = movie_search[0].movieID
        get_movie = ia.get_movie(movie_search_id)

            #if acting_one or acting_two in get_movie:

        ia.update(get_movie, 'release dates')
        date_search = get_movie['release dates'][0]
        index = date_search.rfind(':')
        date_search = date_search[index+1:]
        date_search = date_search.split(' ')
        date_search = date_search[0:3][::-1]

        if len(date_search[2]) < 2:
            date_search[2] = '0' + date_search[2]

        stringz = ""
        if date_search[1] == 'January':
            date_search[1] = '01'
        elif date_search[1] == 'February':
            date_search[1] = '02'
        elif date_search[1] == 'March':
            date_search[1] = '03'
        elif date_search[1] == 'April':
            date_search[1] = '04'
        elif date_search[1] == 'May':
            date_search[1] = '05'
        elif date_search[1] == 'June':
            date_search[1] = '06'
        elif date_search[1] == 'July':
            date_search[1] = '07'
        elif date_search[1] == 'August':
            date_search[1] = '08'
        elif date_search[1] == 'September':
            date_search[1] = '09'
        elif date_search[1] == 'October':
            date_search[1] = '10'
        elif date_search[1] == 'November':
            date_search[1] = '11'
        elif date_search[1] == 'December':
            date_search[1] = '12'

        for i in date_search:
            stringz += i + "-"

        release_date = stringz[:-1]
"""

        for_link = data_row[1]
        for_link = for_link.split(" ")
        output = "https://www.imdb.com/find?q="
        for i in for_link:
            output += i + "+"
        output = output + "&ref_=nv_sr_sm"

        """
        ia = IMDb()
        movie_search = ia.search_movie(data_row[1])
        movie_search_id = movie_search[0].movieID
        get_movie = ia.get_movie(movie_search_id)
        image_link = ""
        image_link += get_movie['cover url']
        """

        describe_movie = float(data_row[8])
        describe_movie_output = ""
        if describe_movie < 5:
            describe_movie_output = ". This terrible movie is directed by "
        elif 5 <= describe_movie < 7:
            describe_movie_output = ". This average movie is directed by "
        elif 7 <= describe_movie < 9:
            describe_movie_output = ". This great movie is directed by "
        elif 9 <= describe_movie <= 10:
            describe_movie_output = ". This amazing movie is directed by "

        metascore_output = ""
        if data_row[11] != "N/A":
            metascore = int(data_row[11])
            if metascore < 50:
                metascore_output = " With a shockingly low Metascore of " + data_row[11] + " this movie straight up stinks!"
            elif 50 <= metascore < 70:
                metascore_output = " With a somewhat decent Metascore of " + data_row[11] + " this movie is watchable."
            elif 70 <= metascore < 90:
                metascore_output = " With a awesome Metascore of " + data_row[11] + " this movie is a must recommend."
            elif 90 <= metascore <= 100:
                metascore_output = " With an almost perfect Metascore of  " + data_row[11] + " this movie is a no brainer."

        revenue_output = ""
        if data_row[10] != "N/A":
            revenue_output = " Showing why " + data_row[1] + " made $" + data_row[10] + " million dollars!"
        else:
            revenue_output = " Enjoy!.... or not"

        running_time_output = ""
        running_time = data_row[7]
        if int(running_time) < 90:
            running_time_output = " With a less than average running time of " + running_time + " minutes, this movie won't take long too watch."
        elif 90 <= int(running_time) < 120:
            running_time_output = " With an average running time of " + running_time + " minutes, this movie will be as long as most."
        elif 120 <= int(running_time):
            running_time_output = " With a longer than average running time of " + running_time + " minutes, this movie needs more of your time so make sure you schedule some time in!"

        # Create Article object.
        article = Article(
            date=date.fromisoformat(release_date),
            title=data_row[1] + " (" + data_row[6] + ") " + "   -   " + str(math.floor(float(data_row[8]))) + "/10",
            first_para=data_row[1] + " came out last year in " + data_row[6] + ". Starring " + data_row[5]
            + describe_movie_output + data_row[4] + " as shown by the following plot: " + data_row[3]
            + metascore_output + running_time_output + revenue_output,
            hyperlink=output,
            image_hyperlink="http://1.bp.blogspot.com/-GQ4m8ee6tCU/UR18yk5lU0I/AAAAAAAABMo/7vMBqhxIjEA/s1600/Logo_Movie+Nights.png",
            id=article_key
        )

        # Add the Article to the repository.
        repo.add_article(article)

    # Create Tag objects, associate them with Articles and add them to the repository.
    for tag_name in tags.keys():
        tag = Tag(tag_name)
        for article_id in tags[tag_name]:
            article = repo.get_article(article_id)
            make_tag_association(article, tag)
        repo.add_tag(tag)


def load_users(data_path: str, repo: MemoryRepository):
    users = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'users.csv')):
        user = User(
            username=data_row[1],
            password=generate_password_hash(data_row[2])
        )
        repo.add_user(user)
        users[data_row[0]] = user
    return users


def load_comments(data_path: str, repo: MemoryRepository, users):
    for data_row in read_csv_file(os.path.join(data_path, 'comments.csv')):
        comment = make_comment(
            comment_text=data_row[3],
            user=users[data_row[1]],
            article=repo.get_article(int(data_row[2])),
            timestamp=datetime.fromisoformat(data_row[4])
        )
        repo.add_comment(comment)


def populate(data_path: str, repo: MemoryRepository):
    # Load articles and tags into the repository.
    load_articles_and_tags(data_path, repo)

    # Load users into the repository.
    users = load_users(data_path, repo)

    # Load comments into the repository.
    load_comments(data_path, repo, users)
