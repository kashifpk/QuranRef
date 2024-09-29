from pydantic import BaseModel

class AyaResultSchema(BaseModel):
    """
    aya_key is a string in the format of "{surah_number}:{aya_number}"

    texts is a dictionary of dictionaries {language: {text_type: text, ...}, ...}
    where the outer dictionary is keyed by language and the inner dictionary is keyed by text type

    example: {"english": {"maududi": "In the name of Allah, the Entirely Merciful, the Especially Merciful."}}
    """

    aya_key: str
    texts: dict[str, dict[str, str]]
