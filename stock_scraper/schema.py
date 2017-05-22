from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class Index(Base):
    __tablename__ = 'indexes'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    code = Column(String(5))
    pages = Column(Integer)
    url = Column(String(1000))

    @classmethod
    def build(cls, row):
        return cls(name=row[0], code=row[1], pages=row[2], url=row[3])


class Share(Base):
    __tablename__ = 'shares'

    id = Column(Integer, primary_key=True)
    code = Column(String(50))
    name = Column(String(50))
    index_id = Column(Integer, ForeignKey('indexes.id'))
    index = relationship(Index, primaryjoin=index_id == Index.id)

    @classmethod
    def build(cls, tree, index):
        code = tree.xpath('td//span')[0].xpath('text()')
        name = tree.xpath('td//a/text()')

        return cls(code=code, name=name, index=index)
