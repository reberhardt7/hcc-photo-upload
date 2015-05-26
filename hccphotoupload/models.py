from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Text,
    Boolean,
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
    uploaded_to_gdrive = Column(Boolean)

    def __init__(self, date_uploaded, original_filename, uploader_ip, content_type, size):
        self.date_uploaded = date_uploaded
        self.original_filename = original_filename
        self.uploader_ip = uploader_ip
        self.content_type = content_type
        self.size = size
        self.uploaded_to_gdrive = False

    def __repr__(self):
        return "<Photo(id={}, original_filename={})>".format(self.id, self.original_filename)

class GDriveAccount(Base):
    __tablename__ = 'gdrive_account'
    id = Column(Integer, primary_key=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    token_expiry = Column(DateTime, nullable=False)

    def __init__(self, access_token, refresh_token, token_expiry):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = token_expiry
