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
