from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True)
    date_uploaded = Column(DateTime)
    original_filename = Column(Text)
    uploader_ip = Column(Text)
    content_type = Column(Text)
    size = Column(Integer)

    def __init__(self, date_uploaded, original_filename, uploader_ip, content_type, size):
        self.date_uploaded = date_uploaded
        self.original_filename = original_filename
        self.uploader_ip = uploader_ip
        self.content_type = content_type
        self.size = size
