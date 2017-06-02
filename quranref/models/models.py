from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    UnicodeText,
    UniqueConstraint,
    Index,
    )

from . import db, Base


# Create your models here.

class Aya(Base):
    "Surah database representation"

    __tablename__ = "ayas"

    #start, ayas, order, rukus, name, tname, ename, type

    id = Column(Integer, primary_key=True)
    surah = Column(Integer)
    aya_number = Column(Integer)
    arabic_text = Column(UnicodeText)

    __table_args__ = (
        UniqueConstraint('surah', 'aya_number', name='_surah_aya_uc'),
        Index('idx_surah_aya', 'surah', 'aya_number', unique=True)
    )

    def get_translation(self, translation_name):
        "Given a translation_name, returns the translation for current Aya"
        
        return db.query(Translation.translation_text).filter_by(
            translation_name=translation_name,
            surah=self.surah,
            aya_number=self.aya_number).first()[0]

    def get_range(self, surah_num, aya_start, aya_end=None):
        "Returns a list of ayas for given surah"
        
        if not aya_end:
            aya_end = aya_start
            
        ayas = db.query(Aya).filter_by(
            surah=surah_num,
            aya_number=aya_num)


class Translation(Base):
    "Quran translation"

    __tablename__ = 'translations'

    translation_name = Column(Unicode, primary_key=True)
    surah = Column(Integer, primary_key=True)
    aya_number = Column(Integer, primary_key=True)
    translation_text = Column(UnicodeText)
