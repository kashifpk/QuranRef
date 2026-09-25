export interface SurahInfo {
    surah_number: number;
    arabic_name: string;
    english_name: string;
    translated_name: string;
    nuzool_location: string;
    nuzool_order: number;
    rukus: number;
    total_ayas: number;
    [x: string]: unknown;
}

export interface AyaTexts {
    [key: string]: { [key: string]: string };
}

export interface AyaInfo {
    aya_key: string;
    texts: AyaTexts;
}

export interface UserInfo {
    id: number;
    email: string;
    name: string;
    picture_url: string;
}

export interface Bookmark {
    id: number;
    bookmark_type: 'reading' | 'note';
    aya_key: string;
    note: string;
    created_at: string;
    updated_at: string;
}

export interface BookmarksData {
    reading: Bookmark | null;
    notes: Bookmark[];
}

export interface CollectionSummary {
    id: number;
    name: string;
    description: string;
    item_count: number;
    aya_keys: string[];
    created_at: string;
    updated_at: string;
}

export interface CollectionItem {
    id: number;
    aya_key: string;
    note: string;
    position: number;
    created_at: string;
}

export interface CollectionDetail {
    id: number;
    name: string;
    description: string;
    created_at: string;
    updated_at: string;
    items: CollectionItem[];
}

export interface TokenSegment {
    form: string;
    tag: string;
    features: string;
}

export interface TokenInfo {
    position: number;
    text: string;
    text_simple: string;
    tag: string;
    root: string | null;
    lemma: string | null;
    features: string;
    segments: TokenSegment[];
    glosses: Record<string, string>;
}

export interface LemmaOccurrence {
    aya_key: string;
    position: number;
    text: string;
    text_simple: string;
    glosses: Record<string, string>;
    aya_text: string;
}

export interface LemmaMeaning {
    gloss: string;
    count: number;
}

export interface LemmaInfo {
    lemma: string;
    pos: string;
    root: string | null;
    count: number;
    meanings: Record<string, LemmaMeaning[]>;
    occurrences: LemmaOccurrence[];
}

export interface RootLemma {
    lemma: string;
    pos: string;
    count: number;
}

export interface RootInfo {
    root: string;
    letters: number;
    count: number;
    lemmas: RootLemma[];
}

export interface WordMorphology {
    lemma: string | null;
    root: string | null;
    pos: string | null;
    count: number;
}

export const POS_LABELS: Record<string, string> = {
    N: 'Noun',
    V: 'Verb',
    P: 'Particle',
};

export interface TopicSummary {
    id: string;
    name: string;
    arabic_name: string;
    aya_count: number;
    thematic: boolean;
    ontology: boolean;
    parent_id: string | null;
    thematic_parent_id: string | null;
    ontology_parent_id: string | null;
}

export interface TopicInfo {
    id: string;
    name: string;
    arabic_name: string;
    description: string;
    wiki_link: string;
    thematic: boolean;
    ontology: boolean;
    aya_count: number;
    parents: TopicSummary[];
    children: TopicSummary[];
    related: TopicSummary[];
}

export interface ThemeInfo {
    id: string;
    theme: string;
    surah_number: number;
    aya_from: number;
    aya_to: number;
    keywords: string;
}

export interface AyaTopics {
    topics: TopicSummary[];
    themes: ThemeInfo[];
}

export interface AyaPage {
    total: number;
    offset: number;
    ayas: AyaInfo[];
}

export interface SimilarAya {
    aya_key: string;
    score: number;
    coverage: number;
    matched_words: number;
    match_words: number[][];
    texts: AyaTexts;
}

export interface PhraseInfo {
    id: string;
    text: string;
    source_aya: string;
    aya_count: number;
    ranges: number[][];
    aya_keys: string[];
}

export interface RelatedInfo {
    similar: SimilarAya[];
    phrases: PhraseInfo[];
}

export type UnitKind = 'juz' | 'hizb' | 'rub' | 'manzil' | 'ruku';

export interface StructureUnit {
    number: number;
    verses_count: number;
    first_verse_key: string;
    last_verse_key: string;
    verse_mapping: Record<string, string>;
    surah_ruku_number?: number;
}

export type Structure = Record<UnitKind, StructureUnit[]>;

export interface SurahMarker {
    aya_number: number;
    juz_start: number | null;
    hizb_start: number | null;
    rub_start: number | null;
    manzil_start: number | null;
    ruku_start: number | null;
    sajda: string | null;
}

export interface SurahInfoText {
    surah_number: number;
    language: string;
    available: string[];
    text: string;
    short_text: string;
}

export interface TafsirResource {
    slug: string;
    name: string;
    language: string;
    author: string;
    source: string;
    license: string;
}

export interface TafsirPassage {
    slug: string;
    name: string;
    language: string;
    aya_key: string;
    from_key: string;
    to_key: string;
    aya_keys: string[];
    text: string;
}
