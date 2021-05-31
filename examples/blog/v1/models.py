import json

from sqlalchemy.orm import declarative_base, relationship, Session, backref
from sqlalchemy import Table, String, Column, Integer, Text, ForeignKey, create_engine, select, Boolean

Base = declarative_base()
engine = create_engine("mysql+pymysql://root:password@localhost:3306/test")


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), nullable=False, unique=True)
    pwd = Column(String(128), nullable=False)
    articles = relationship('Article', back_populates="author")
    is_superuser = Column(Boolean, default=False, nullable=False)


articles_categories = Table('articles_categories',
                            Base.metadata,
                            Column('article_id', Integer, ForeignKey("article.id"),
                                   primary_key=True),
                            Column('category_id', Integer, ForeignKey("category.id"),
                                   primary_key=True),
                            )


class Article(Base):
    __tablename__ = "article"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(30), nullable=False)
    subtitle = Column(String(50), nullable=True)
    author_id = Column(Integer, ForeignKey('user.id', name="author_id"))
    author = relationship('User', back_populates="articles")
    description = Column(String(200), nullable=True)
    content = Column(Text, nullable=False, default="")
    categories = relationship('Category', secondary=articles_categories, back_populates="articles")

    def json(self):
        obj = {
            "id": self.id,
            "title": self.title,
            "subtitle": self.subtitle,
            "author_id": self.author_id,
            "description": self.description,
            "content": self.content,
        }
        categories = []
        for category in self.categories:
            category_obj = {"id": category.id, "name": category.name}
            categories.append(category_obj)
        obj["categories"] = categories

        if self.author is not None:
            obj["author"] = self.author.username
        return obj


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, unique=True)
    articles = relationship('Article', secondary=articles_categories, back_populates="categories")


# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
# with Session(engine) as session:
#     results = session.execute(select(Article))
#     articles = results.all()
#     article = articles[0][0] #type:Article
#     print(article.categories)
#     # print(article.title)
