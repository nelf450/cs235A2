from datetime import date

from movie.domain.model import User, Article, Tag, make_comment, make_tag_association, ModelException

import pytest


@pytest.fixture()
def article():
    return Article(
        date.fromisoformat('2007-02-02'),
        'The Devil Wears Prada (2006) - 6/10','The Devil Wears Prada came out last year in 2006. Starring Anne Hathaway'
                                              ', Meryl Streep, Adrian Grenier, Emily Blunt. This average movie is '
                                              'directed by David Frankel as shown by the following plot: A smart but '
                                              'sensible new graduate lands a job as an assistant to Miranda Priestly, '
                                              'the demanding editor-in-chief of a high fashion magazine. With a '
                                              'somewhat decent Metascore of 62 this movie is watchable. '
                                              'With an average running time of 109 minutes, this movie will be as '
                                              'long as most. Showing why The Devil Wears Prada made $124.73 million '
                                              'dollars!',
        'https://www.imdb.com/find?q=The+Devil+Wears+Prada+&ref_=nv_sr_sm',
        'http://1.bp.blogspot.com/-GQ4m8ee6tCU/UR18yk5lU0I/AAAAAAAABMo/7vMBqhxIjEA/s1600/Logo_Movie+Nights.png'
    )


@pytest.fixture()
def user():
    return User('dbowie', '1234567890')


@pytest.fixture()
def tag():
    return Tag('Action')


def test_user_construction(user):
    assert user.username == 'dbowie'
    assert user.password == '1234567890'
    assert repr(user) == '<User dbowie 1234567890>'

    for comment in user.comments:
        # User should have an empty list of Comments after construction.
        assert False


def test_article_construction(article):
    assert article.id is None
    assert article.date == date.fromisoformat('2007-02-02')
    assert article.title == 'The Devil Wears Prada (2006) - 6/10'
    assert article.first_para == 'The Devil Wears Prada came out last year in 2006. Starring Anne Hathaway, ' \
                                 'Meryl Streep, Adrian Grenier, Emily Blunt. This average movie is ' \
                                 'directed by David Frankel as shown by the following plot: A smart but ' \
                                 'sensible new graduate lands a job as an assistant to Miranda Priestly, ' \
                                 'the demanding editor-in-chief of a high fashion magazine. With a ' \
                                 'somewhat decent Metascore of 62 this movie is watchable. ' \
                                 'With an average running time of 109 minutes, this movie will be as ' \
                                 'long as most. Showing why The Devil Wears Prada made $124.73 million dollars!'
    assert article.hyperlink == 'https://www.imdb.com/find?q=The+Devil+Wears+Prada+&ref_=nv_sr_sm'
    assert article.image_hyperlink == 'http://1.bp.blogspot.com/-GQ4m8ee6tCU/UR18yk5lU0I/AAAAAAAABMo/7vMBqhxIjEA/s1600/Logo_Movie+Nights.png'

    assert article.number_of_comments == 0
    assert article.number_of_tags == 0


def test_article_less_than_operator():
    article_1 = Article(
        date.fromisoformat('2020-03-15'), None, None, None, None
    )

    article_2 = Article(
        date.fromisoformat('2020-04-20'), None, None, None, None
    )

    assert article_1 < article_2


def test_tag_construction(tag):
    assert tag.tag_name == 'Action'

    for article in tag.tagged_articles:
        assert False

    assert not tag.is_applied_to(Article(None, None, None, None, None, None))


def test_make_comment_establishes_relationships(article, user):
    comment_text = 'Awesome Movie!'
    comment = make_comment(comment_text, user, article)

    # Check that the User object knows about the Comment.
    assert comment in user.comments

    # Check that the Comment knows about the User.
    assert comment.user is user

    # Check that Article knows about the Comment.
    assert comment in article.comments

    # Check that the Comment knows about the Article.
    assert comment.article is article


def test_make_tag_associations(article, tag):
    make_tag_association(article, tag)

    # Check that the Article knows about the Tag.
    assert article.is_tagged()
    assert article.is_tagged_by(tag)

    # check that the Tag knows about the Article.
    assert tag.is_applied_to(article)
    assert article in tag.tagged_articles


def test_make_tag_associations_with_article_already_tagged(article, tag):
    make_tag_association(article, tag)

    with pytest.raises(ModelException):
        make_tag_association(article, tag)
