from django.core.management.base import BaseCommand
from forum_app.models import *
from random import choice, randint


class Command(BaseCommand):
    def handle(self, *args, **options):
        union = set()
        articles = set()
        comments = set()
        for i in range(500):
            print(f"creating user {i + 1}")
            u = User.objects.create_user(f"auto_user_{i}", "autopass")
            for j in range(randint(0, 3)):
                a = Article(author=u, title=f"Title_{i}_{j}")
                a.save()
                articles.add(a)
                union.add(a)
            if len(articles) > 10:
                for j in range(randint(0, 10)):
                    a = choice(tuple(articles))
                    c = Comment(article_parent=a, author=u, text="I'm bot")
                    c.save()
                    comments.add(c)
                    union.add(c)
            if len(comments) > 10:
                for j in range(randint(0, 10)):
                    a = choice(tuple(comments))
                    c = Comment(comment_parent=a, author=u, text="I'm bot")
                    c.save()
                    comments.add(c)
                    union.add(c)

            if len(union) > 30:
                for j in range(randint(0, 30)):
                    p = choice(tuple(union))
                    try:
                        type = 'L' if randint(0, 1) else 'D'
                        if p is Article:
                            c = Activity(author=u, article_parent=p,
                                         activity_type=type)
                        else:
                            c = Activity(author=u, comment_parent=p,
                                         activity_type=type)
                        c.save()
                    except:
                        pass
