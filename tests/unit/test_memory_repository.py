from datetime import date, datetime
from typing import List

import pytest

from movie.domain.model import User, Article, Tag, Comment, make_comment
from movie.adapters.repository import RepositoryException


def test_repository_can_add_a_user(in_memory_repo):
    user = User('Dave', '123456789')
    in_memory_repo.add_user(user)

    assert in_memory_repo.get_user('Dave') is user


def test_repository_can_retrieve_a_user(in_memory_repo):
    user = in_memory_repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')


def test_repository_does_not_retrieve_a_non_existent_user(in_memory_repo):
    user = in_memory_repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_article_count(in_memory_repo):
    number_of_articles = in_memory_repo.get_number_of_articles()

    # Check that the query returned 6 Articles.
    assert number_of_articles == 1000


def test_repository_can_add_article(in_memory_repo):
    article = Article(
        date.fromisoformat('2007-02-02'),
        'The Devil Wears Prada (2006) - 6/10',
        'The Devil Wears Prada came out last year in 2006. Starring Anne Hathaway'
        ', Meryl Streep, Adrian Grenier, Emily Blunt. This average movie is '
        'directed by David Frankel as shown by the following plot: A smart but '
        'sensible new graduate lands a job as an assistant to Miranda Priestly, '
        'the demanding editor-in-chief of a high fashion magazine. With a '
        'somewhat decent Metascore of 62 this movie is watchable. '
        'With an average running time of 109 minutes, this movie will be as '
        'long as most. Showing why The Devil Wears Prada made $124.73 million '
        'dollars!',
        'https://www.imdb.com/find?q=The+Devil+Wears+Prada+&ref_=nv_sr_sm',
        'http://1.bp.blogspot.com/-GQ4m8ee6tCU/UR18yk5lU0I/AAAAAAAABMo/7vMBqhxIjEA/s1600/Logo_Movie+Nights.png', 298
    )
    in_memory_repo.add_article(article)

    assert in_memory_repo.get_article(298) is article


def test_repository_can_retrieve_article(in_memory_repo):
    article = in_memory_repo.get_article(1)

    # Check that the Article has the expected title.
    assert article.title == 'Guardians of the Galaxy (2014)    -   8/10'

    # Check that the Article is commented as expected.
    comment_one = [comment for comment in article.comments if comment.comment == 'Boo!'][
        0]
    comment_two = [comment for comment in article.comments if comment.comment == 'I love this movie!'][0]

    assert comment_one.user.username == 'fmercury'
    assert comment_two.user.username == "thorke"

    # Check that the Article is tagged as expected.
    assert article.is_tagged_by(Tag('Action'))
    assert article.is_tagged_by(Tag('Adventure'))


def test_repository_does_not_retrieve_a_non_existent_article(in_memory_repo):
    article = in_memory_repo.get_article(1001)
    assert article is None


def test_repository_can_retrieve_articles_by_date(in_memory_repo):
    articles = in_memory_repo.get_articles_by_date(date(2007, 2, 2))

    # Check that the query returned 3 Articles.
    assert len(articles) == 1


def test_repository_does_not_retrieve_an_article_when_there_are_no_articles_for_a_given_date(in_memory_repo):
    articles = in_memory_repo.get_articles_by_date(date(2020, 3, 8))
    assert len(articles) == 0


def test_repository_can_retrieve_tags(in_memory_repo):
    tags: List[Tag] = in_memory_repo.get_tags()

    assert len(tags) == 20

    tag_one = [tag for tag in tags if tag.tag_name == 'Action'][0]
    tag_two = [tag for tag in tags if tag.tag_name == 'Adventure'][0]
    tag_three = [tag for tag in tags if tag.tag_name == 'Sci-Fi'][0]
    tag_four = [tag for tag in tags if tag.tag_name == 'Comedy'][0]

    assert tag_one.number_of_tagged_articles > 1
    assert tag_two.number_of_tagged_articles > 1
    assert tag_three.number_of_tagged_articles > 1
    assert tag_four.number_of_tagged_articles > 1


def test_repository_can_get_first_article(in_memory_repo):
    article = in_memory_repo.get_first_article()
    assert article.title == 'The Devil Wears Prada (2006)    -   6/10'


def test_repository_can_get_last_article(in_memory_repo):
    article = in_memory_repo.get_last_article()
    assert article.title == 'Ice Age: Collision Course (2016)    -   5/10'


def test_repository_can_get_articles_by_ids(in_memory_repo):
    articles = in_memory_repo.get_articles_by_id([2, 5, 6])

    assert len(articles) == 3
    assert articles[
               0].title == 'Prometheus (2012)    -   7/10'
    assert articles[1].title == "Suicide Squad (2016)    -   6/10"
    assert articles[2].title == 'The Great Wall (2016)    -   6/10'


def test_repository_does_not_retrieve_article_for_non_existent_id(in_memory_repo):
    articles = in_memory_repo.get_articles_by_id([2, 5])

    assert len(articles) == 2
    assert articles[
               0].title == 'Prometheus (2012)    -   7/10'
    assert articles[1].title == "Suicide Squad (2016)    -   6/10"


def test_repository_returns_an_empty_list_for_non_existent_ids(in_memory_repo):
    articles = in_memory_repo.get_articles_by_id([0, 10001])

    assert len(articles) == 0


def test_repository_returns_article_ids_for_existing_tag(in_memory_repo):
    article_ids = in_memory_repo.get_article_ids_for_tag('Sport')

    assert article_ids == [195, 311,338,368,378,382,494,549,575,585,587,594,597,831,850,897,936,975]


def test_repository_returns_an_empty_list_for_non_existent_tag(in_memory_repo):
    article_ids = in_memory_repo.get_article_ids_for_tag('United States')

    assert len(article_ids) == 0


def test_repository_returns_date_of_previous_article(in_memory_repo):
    article = in_memory_repo.get_article(870)
    previous_date = in_memory_repo.get_date_of_previous_article(article)

    assert previous_date.isoformat() == '2007-02-02'


def test_repository_returns_none_when_there_are_no_previous_articles(in_memory_repo):
    article = in_memory_repo.get_article(298)
    previous_date = in_memory_repo.get_date_of_previous_article(article)

    assert previous_date is None


def test_repository_returns_date_of_next_article(in_memory_repo):
    article = in_memory_repo.get_article(298)
    next_date = in_memory_repo.get_date_of_next_article(article)

    assert next_date.isoformat() == '2007-02-07'


def test_repository_returns_none_when_there_are_no_subsequent_articles(in_memory_repo):
    article = in_memory_repo.get_article(297)
    next_date = in_memory_repo.get_date_of_next_article(article)

    assert next_date is None


def test_repository_can_add_a_tag(in_memory_repo):
    tag = Tag('Motoring')
    in_memory_repo.add_tag(tag)

    assert tag in in_memory_repo.get_tags()


def test_repository_can_add_a_comment(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    article = in_memory_repo.get_article(2)
    comment = make_comment("Wow!", user, article)

    in_memory_repo.add_comment(comment)

    assert comment in in_memory_repo.get_comments()


def test_repository_does_not_add_a_comment_without_a_user(in_memory_repo):
    article = in_memory_repo.get_article(2)
    comment = Comment(None, article, "Wow!", datetime.today())

    with pytest.raises(RepositoryException):
        in_memory_repo.add_comment(comment)


def test_repository_does_not_add_a_comment_without_an_article_properly_attached(in_memory_repo):
    user = in_memory_repo.get_user('thorke')
    article = in_memory_repo.get_article(2)
    comment = Comment(None, article, "Wow!", datetime.today())

    user.add_comment(comment)

    with pytest.raises(RepositoryException):
        # Exception expected because the Article doesn't refer to the Comment.
        in_memory_repo.add_comment(comment)


def test_repository_can_retrieve_comments(in_memory_repo):
    assert len(in_memory_repo.get_comments()) == 3



