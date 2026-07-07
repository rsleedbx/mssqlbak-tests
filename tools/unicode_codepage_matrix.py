"""Code-page / collation matrix for the G55 unicode_codepage_coverage fixture.

Each entry gives a ``(python_codec, sql_collation, windows_lcid, script_name,
varchar_sample, nvarchar_extra)`` tuple.

``varchar_sample``
    A Unicode string whose characters are representable in the column's code
    page.  SQL Server converts N'...' Unicode literals to the column's code
    page on INSERT, replacing unmappable characters with ``?``.  Samples are
    taken directly from the Unicode 2.0 and 3.2 test pages:
        https://www.cogsci.ed.ac.uk/~richard/unicode-sample.html
        https://www.cogsci.ed.ac.uk/~richard/unicode-sample-3-2.html

``nvarchar_extra``
    Additional characters from those script blocks that fall outside the code
    page's range (stored in the companion NVARCHAR column only, for
    round-trip comparison in future tests).

Purpose
-------
The fixture exists to resolve G55: the exact bit layout of
``syscolpars.collationid`` for non-UTF-8, non-cp1252 collations.  After the
BAK is created, ``tools/make_unicode_codepage_fixture.py`` probes each column's
``collation_id`` and prints the values so the LCID bit position can be
determined empirically by XOR-ing the Latin1 baseline (0x3400D008) with
each discovered value.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CodepageEntry:
    python_codec: str         # Python codec name (e.g. "cp1251")
    sql_collation: str        # SQL Server COLLATE name (e.g. "Cyrillic_General_CI_AS")
    windows_lcid: int         # Expected Windows LCID (to verify after decode)
    script_name: str          # Human-readable description
    varchar_sample: str       # Characters encodable in the code page
    nvarchar_extra: str = ""  # Unicode-only extras (stored in NVARCHAR column)


# Samples drawn from the Unicode 2.0 and 3.2 test pages (cogsci.ed.ac.uk).
# Characters are chosen to exercise both the 0x80–0xBF and 0xC0–0xFF byte
# ranges of each code page so a round-trip test can confirm correct decoding.
CODEPAGE_ENTRIES: list[CodepageEntry] = [
    # ---- Windows code pages (SBCS) ----
    CodepageEntry(
        python_codec="cp1250",
        sql_collation="Polish_CI_AS",
        windows_lcid=0x0415,
        script_name="Central European (Polish / Czech / Hungarian)",
        # Latin Extended-A characters that cp1250 encodes
        varchar_sample=(
            "Ą ą Ć ć Č č Ď ď Ě ě Ł ł Ń ń Ő ő Ř ř Ś ś Š š "
            "Ź ź Ż ż Ž ž Ŕ ŕ Ŗ ŗ Ÿ ź"
        ),
    ),
    CodepageEntry(
        python_codec="cp1251",
        sql_collation="Cyrillic_General_CI_AS",
        windows_lcid=0x0419,
        script_name="Russian / Cyrillic",
        # Full Cyrillic block (Unicode sample page §Cyrillic)
        varchar_sample=(
            "А Б В Г Д Е Ж З И Й К Л М Н О П "
            "Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я "
            "а б в г д е ж з и й к л м н о п "
            "р с т у ф х ц ч ш щ ъ ы ь э ю я "
            "Ё ё"
        ),
        nvarchar_extra="Ѐ Ђ Ѓ Є Ѕ І Ї Ј Љ Њ Ћ Ќ Ў Џ",
    ),
    CodepageEntry(
        python_codec="cp1253",
        sql_collation="Greek_CI_AS",
        windows_lcid=0x0408,
        script_name="Greek",
        # Greek and Coptic block (Unicode sample page §Greek)
        varchar_sample=(
            "Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω "
            "α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ ς σ τ υ φ χ ψ ω "
            "Ά Έ Ή Ί Ό Ύ Ώ ά έ ή ί ό ύ ώ ΐ ΰ"
        ),
    ),
    CodepageEntry(
        python_codec="cp1254",
        sql_collation="Turkish_CI_AS",
        windows_lcid=0x041F,
        script_name="Turkish",
        # Turkish-specific letters; cp1254 otherwise overlaps Latin-1 Supplement
        varchar_sample="Ğ ğ İ ı Ş ş Ç ç Ö ö Ü ü",
    ),
    CodepageEntry(
        python_codec="cp1255",
        sql_collation="Hebrew_CI_AS",
        windows_lcid=0x040D,
        script_name="Hebrew",
        # Hebrew block (Unicode sample page §Hebrew)
        varchar_sample=(
            "א ב ג ד ה ו ז ח ט י ך כ ל ם מ ן נ ס ע ף פ ץ צ ק ר ש ת"
        ),
    ),
    CodepageEntry(
        python_codec="cp1256",
        sql_collation="Arabic_CI_AS",
        windows_lcid=0x0401,
        script_name="Arabic",
        # Arabic letters encodable in cp1256 (Unicode sample page §Arabic)
        varchar_sample=(
            "ء آ أ ؤ إ ئ ا ب ة ت ث ج ح خ "
            "د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن ه و ى ي"
        ),
    ),
    CodepageEntry(
        python_codec="cp1257",
        sql_collation="Lithuanian_CI_AS",
        windows_lcid=0x0427,
        script_name="Baltic / Lithuanian",
        # Baltic-specific accented Latin letters (Latin Extended-A)
        varchar_sample=(
            "Ā ā Č č Ē ē Ģ ģ Ī ī Ķ ķ Ļ ļ Ņ ņ Š š Ū ū Ž ž"
        ),
    ),
    CodepageEntry(
        python_codec="cp1258",
        sql_collation="Vietnamese_CI_AS",
        windows_lcid=0x042A,
        script_name="Vietnamese",
        # Vietnamese tone-marked Latin letters (cp1258 uses combining marks)
        varchar_sample=(
            "à á â ã ả ạ ặ ắ ằ ẳ ẵ "
            "è é ê ề ế ể ễ ệ "
            "ì í ỉ ị "
            "ò ó ô ơ ờ ớ ở ỡ ợ"
        ),
    ),
    CodepageEntry(
        python_codec="cp874",
        sql_collation="Thai_CI_AS",
        windows_lcid=0x041E,
        script_name="Thai",
        # Thai consonants and vowels (Unicode sample page §Thai)
        varchar_sample=(
            "ก ข ฃ ค ฅ ฆ ง จ ฉ ช ซ ฌ ญ ฎ ฏ "
            "ฐ ฑ ฒ ณ ด ต ถ ท ธ น บ ป ผ ฝ พ ฟ ภ ม ย ร ล ว ศ ษ ส ห อ ฮ "
            "ะ า ิ ี ึ ื ุ ู เ แ โ ใ ไ ๐ ๑ ๒ ๓ ๔ ๕ ๖ ๗ ๘ ๙"
        ),
    ),
    # ---- Windows code pages (DBCS — double-byte character sets) ----
    CodepageEntry(
        python_codec="cp932",
        sql_collation="Japanese_CI_AS",
        windows_lcid=0x0411,
        script_name="Japanese (Shift-JIS / cp932)",
        # Hiragana + Katakana (Unicode sample page §Hiragana / §Katakana)
        varchar_sample=(
            "あ い う え お か き く け こ さ し す せ そ た ち つ て と な に ぬ ね の "
            "ア イ ウ エ オ カ キ ク ケ コ サ シ ス セ ソ タ チ ツ テ ト ナ ニ ヌ ネ ノ"
        ),
        nvarchar_extra="ぁ ぃ ぅ ぇ ぉ ヵ ヶ",
    ),
    CodepageEntry(
        python_codec="cp936",
        sql_collation="Chinese_PRC_CI_AS",
        windows_lcid=0x0804,
        script_name="Chinese Simplified (GBK / cp936)",
        # CJK Unified Ideographs (Unicode sample page §CJK Unified Ideographs)
        varchar_sample=(
            "一 丁 七 万 三 上 下 中 不 与 东 两 严 久 之 也 "
            "乘 乙 九 乞 书 乡 买 乱 乳 人 大 小 国 地 年 生"
        ),
    ),
    CodepageEntry(
        python_codec="cp949",
        sql_collation="Korean_Wansung_CI_AS",
        windows_lcid=0x0412,
        script_name="Korean (EUC-KR / cp949)",
        # Hangul syllables (Unicode sample page §Hangul Syllables)
        varchar_sample=(
            "가 각 간 갈 감 갑 강 개 거 건 결 경 "
            "고 공 관 교 구 국 군 그 기 길 김 나 날 남 내 너 년"
        ),
    ),
    CodepageEntry(
        python_codec="cp950",
        sql_collation="Chinese_Taiwan_Stroke_CI_AS",
        windows_lcid=0x0404,
        script_name="Chinese Traditional (Big5 / cp950)",
        # CJK Ideographs — Traditional Chinese subset
        varchar_sample=(
            "一 丁 七 萬 三 上 下 中 不 與 東 兩 嚴 久 之 也 "
            "乘 乙 九 乞 書 鄉 買 亂 乳 人 大 小 國 地 年 生"
        ),
    ),
]

# Convenience: the Latin1_General baseline already known from empirical probing.
# (GeneralHospital.bak — all varchar columns)
LATIN1_GENERAL_CI_AS_COLLATION_ID = 0x3400D008
