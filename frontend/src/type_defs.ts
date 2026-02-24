export interface SurahInfo {
    _key: string;
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
