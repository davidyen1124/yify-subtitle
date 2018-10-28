from .config import NORMAL


def sublog(text, doc=None):
    if doc:
        doc.log(text)
    print(text)


class SubDoc:
    def __init__(self):
        self.lines = []

    def log(self, line, type=NORMAL):
        self.lines.append(type.format(line))

    def get(self):
        l = '\n'.join(self.lines)
        self.lines = []
        return l


encodings = (
    ('utf8', ".+ utf8"),  # WIN_1250
    ('WIN_1250', "windows-1250"),  # WIN_1250
    ('WIN_1251', "windows-1251"),  # WIN_1251
    ('WIN_1252', "windows-1252"),  # WIN_1252
    ('WIN_1253', "windows-1253"),  # WIN_1253
    ('WIN_1254', "windows-1254"),  # WIN_1254
    ('WIN_1255', "windows-1255"),  # WIN_1255
    ('WIN_1256', "windows-1256"),  # WIN_1256
    ('WIN_1257', "windows-1257"),  # WIN_1257
    ('WIN_1258', "windows-1258"),  # WIN_1258
    ('ISO_8859_1', "latin1 ISO_8859-1 ISO-8859-1 CP819 IBM819 csISOLatin1 iso-ir-100 l1"),
    # ISO_8859_1
    ('ISO_8859_2', "latin2 ISO_8859-2 ISO-8859-2 csISOLatin2 iso-ir-101 l2"),  # ISO_8859_2
    ('ISO_8859_3', "latin3 ISO_8859-3 ISO-8859-3 csISOLatin3 iso-ir-109 l3"),  # ISO_8859_3
    ('ISO_8859_4', "latin4 ISO_8859-4 ISO-8859-4 csISOLatin4 iso-ir-110 l4"),  # ISO_8859_4
    ('ISO_8859_5', "cyrillic ISO_8859-5 ISO-8859-5 csISOLatinCyrillic iso-ir-144"),  # ISO_8859_5
    ('ISO_8859_6', "arabic ISO_8859-6 ISO-8859-6 csISOLatinArabic iso-ir-127 ASMO-708 ECMA-114"),
    # ISO_8859_6
    ('ISO_8859_7', "greek ISO_8859-7 ISO-8859-7 csISOLatinGreek greek8 iso-ir-126 ELOT_928 ECMA-118"),
    # ISO_8859_7
    ('ISO_8859_8', "hebrew ISO_8859-8 ISO-8859-8 csISOLatinHebrew iso-ir-138"),  # ISO_8859_8
    ('ISO_8859_9', "latin5 ISO_8859-9 ISO-8859-9 csISOLatin5 iso-ir-148 l5"),  # ISO_8859_9
    ('ISO_8859_10', "latin6 ISO_8859-10 ISO-8859-10 csISOLatin6 iso-ir-157 l6"),  # //ISO_8859_10
    ('ISO_8859_11', "ISO_8859-11 ISO-8859-11"),  # //ISO_8859_11
    ('ISO_8859_13', "ISO_8859-13 ISO-8859-13"),  # ISO_8859_13
    ('ISO_8859_14', "iso-celtic latin8 ISO_8859-14 ISO-8859-14 18 iso-ir-199"),  # ISO_8859_14
    ('ISO_8859_15', "Latin-9 ISO_8859-15 ISO-8859-15"),  # ISO_8859_15
    ('ISO_8859_16', "latin10 ISO_8859-16 ISO-8859-16 110 iso-ir-226"),  # //ISO_8859_16
    ('DOS_437', "IBM437 cp437 437 csPC8CodePage437"),  # DOS_437
    ('DOS_720', "IBM720 cp720 oem720 720"),  # DOS_720
    ('DOS_737', "IBM737 cp737 oem737 737"),  # DOS_737
    ('DOS_775', "IBM775 cp775 oem775 775"),  # DOS_775
    ('DOS_850', "IBM850 cp850 oem850 850"),  # DOS_850
    ('DOS_852', "IBM852 cp852 oem852 852"),  # DOS_852
    ('DOS_855', "IBM855 cp855 oem855 855 csIBM855"),  # DOS_855
    ('DOS_857', "IBM857 cp857 oem857 857"),  # DOS_857
    ('DOS_858', "IBM858 cp858 oem858 858"),  # DOS_858
    ('DOS_860', "IBM860 cp860 oem860 860"),  # DOS_860
    ('DOS_861', "IBM861 cp861 oem861 861"),  # DOS_861
    ('DOS_862', "IBM862 cp862 oem862 862"),  # DOS_862
    ('DOS_863', "IBM863 cp863 oem863 863"),  # DOS_863
    ('DOS_865', "IBM865 cp865 oem865 865"),  # DOS_865
    ('DOS_866', "IBM866 cp866 oem866 866"),  # DOS_866
    ('DOS_869', "IBM869 cp869 oem869 869"),  # DOS_869
    ('BIG5', "big5 csBig5"),  # BIG5
    ('GB2312', "gb2312 gbk csGB2312 gb18030"),  # GB2312
    ('SHIFT_JIS', "Shift_JIS MS_Kanji csShiftJIS csWindows31J"),  # SHIFT_JIS
    ('KOREAN_WIN', "windows-949 korean"),  # KOREAN_WIN
    ('EUC_KR', "euc-kr csEUCKR"),  # EUC_KR
    ('TIS_620', "tis-620"),  # TIS_620
    ('MAC_CYRILLIC', "x-mac-cyrillic xmaccyrillic"),  # MAC_CYRILLIC
    ('KOI8U_CYRILLIC', "koi8_u"),  # KOI8U_CYRILLIC
    ('KOI8R_CYRILLIC', "koi8_r csKOI8R")  # KOI8R_CYRILLIC
)  #


def get_encodings(name):
    return [encoding for encoding, keywords in encodings if name in keywords or ".+" in keywords]

class EncodingError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
