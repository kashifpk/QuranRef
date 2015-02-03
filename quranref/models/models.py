from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    UnicodeText,
    UniqueConstraint,
    Index
    )

from . import db, Base


# Create your models here.

class Aya(Base):
    "Surah database representation"
    
    __tablename__ = "ayas"
    
    #start, ayas, order, rukus, name, tname, ename, type
    
    id = Column(Integer, primary_key=True)
    surah = Column(Integer)
    aya_number = Column(Unicode(100))
    arabic_text = Column(UnicodeText)
    
    __table_args__ = (
        UniqueConstraint('surah', 'aya_number', name='_surah_aya_uc'),
        Index('idx_surah_aya', 'surah', 'aya_number', unique=True)
    )


