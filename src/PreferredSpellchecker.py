# -*- coding: utf-8 -*-
"""Academy-preferred Persian spelling checks for LibreOffice Writer."""

import json
import os
import re
import unicodedata

import uno
import unohelper
from com.sun.star.lang import Locale, XServiceInfo, XServiceName, XServiceDisplayName
from com.sun.star.linguistic2 import XProofreader, XSupportedLocales


ZWNJ = "\u200c"
TOKEN_RE = re.compile(r"[\w\u200c\u200e\u200f\u0640\u064b-\u065f\u0670]+", re.UNICODE)
NORMALIZE_MARKS_RE = re.compile(r"[\u064b-\u065f\u0670\u200e\u200f\u0640]")
HA_SUFFIXES = (
    "هایشان", "هایمان", "هایتان", "هایم", "هایت", "هایش",
    "هایی", "هاست", "های", "ها",
)
MI_PREFIXES = ("نمی", "همی", "می")
EMPHATIC_HAMI_FOLLOWING = {"نیست"}
DEMONSTRATIVE_ATTACHED_FORMS = {
    "اینطور": "این" + ZWNJ + "طور",
    "آنطور": "آن" + ZWNJ + "طور",
    "اینگونه": "این" + ZWNJ + "گونه",
    "آنگونه": "آن" + ZWNJ + "گونه",
}
DEMONSTRATIVE_PARTS = {"طور", "گونه"}
SAME_FORMS_ATTACHED = {
    "همانجا": "همان" + ZWNJ + "جا",
    "همینجا": "همین" + ZWNJ + "جا",
    "همانجور": "همان" + ZWNJ + "جور",
    "همینجور": "همین" + ZWNJ + "جور",
    "همانگونه": "همان" + ZWNJ + "گونه",
    "همینگونه": "همین" + ZWNJ + "گونه",
}
UNJOINABLE_ENDINGS = set("اآدذرزژو")
DEGREE_SUFFIXES = ("ترین", "تر")
DEGREE_EXCEPTIONS = {"بهتر", "کهتر", "مهتر", "بیشتر", "کمتر", "کلانتر"}
HARE_COMPOUND_STEMS = {
    "آینه", "ازگاهی", "چند", "طور", "کدام", "کس", "که", "گاه", "گونه", "یک",
}
HARE_COMPOUND_FORMS = {"هر" + stem for stem in HARE_COMPOUND_STEMS}
HIC_COMPOUND_STEMS = {"کدام", "کس", "گاه", "گونه", "یک"}
HIC_COMPOUND_FORMS = {"هیچ" + ZWNJ + stem for stem in HIC_COMPOUND_STEMS}
BI_PREFIX_EXCEPTIONS = {
    "بیجا", "بیچاره", "بیخود", "بیداد", "بیدل", "بیراه", "بیزار",
    "بیعار", "بیکار", "بینوا", "بیهوش", "بیهوده", "بیگانه", "بیشتر",
    # Lexicalized words, names, or verb forms that only resemble "بی + stem".
    "بیاد", "بیارجمند", "بیتا", "بیتایی", "بیتل", "بیجار", "بیجاری",
    "بیدار", "بیستم", "بیستون", "بیشام", "بیشاپور", "بیشه", "بیرونی",
    "بیله", "بیلک", "بیلیون", "بیمار", "بیماری", "بیمه", "بین", "بینا",
    "بینال", "بینه", "بینی", "بیهاری", "بیژن", "بیکاره", "بیکاری",
    "بیسینگر", "بیگاری", "بیگاه", "بیگل", "بیگلو", "بیگم", "بیگودی",
}
BI_PREFIX_SPACE_BASES = {
    "تردید", "توجه", "حاصل", "حساب", "حوصله", "جهت", "قرار",
    "باک", "تاب", "جان", "حال", "حد", "رحم", "رنگ", "روح", "شمار",
    "طرف", "سواد", "گمان", "رویه", "کران",
}
ZWNJ_SUFFIXES = ("آگین", "آسا", "باره", "جات", "فام", "وش", "سان", "وار")
ATTACHED_SUFFIXES = ("واره",)
WAR_SUFFIX_EXCEPTIONS = {
    "بزرگوار", "خانوار", "راهوار", "رهوار", "سوگوار", "شاهوار",
    "شهوار", "عیالوار", "ماهوار",
}
SAN_SUFFIX_EXCEPTIONS = {"همسان", "یکسان"}
CONDITIONAL_ZWNJ_SUFFIXES = ("گری", "گر")
CONDITIONAL_ZWNJ_ROOTS = {"توجیه", "لاابالی"}
JOINED_LEXICALIZED_SUFFIX_EXCEPTIONS = {
    "سفارتخانه", "غسالخانه", "کتابخانه", "گلخانه", "میخانه",
    "اساسنامه", "بخشنامه", "دانشنامه", "سالنامه", "شاهنامه",
    "فصلنامه", "قطعنامه", "قولنامه", "ماهنامه",
}
BI_PREFIX_ATTACHED_EXAMPLES = {
    "بیچونوچرا": "بی" + ZWNJ + "چون" + ZWNJ + "و" + ZWNJ + "چرا",
    "بیچون" + ZWNJ + "وچرا": "بی" + ZWNJ + "چون" + ZWNJ + "و" + ZWNJ + "چرا",
}
SINGLE_VERB_PREFIX_EXAMPLES = {
    ("ب", "آموز"): "بیاموز",
    ("م", "افکن"): "میفکن",
    ("م", "آزار"): "میازار",
    ("ن", "آفرید"): "نیافرید",
}
BE_HALFSPACE_ATTACHED_FORMS = {
    "بهخصوص": "به" + ZWNJ + "خصوص",
    "بخصوص": "به" + ZWNJ + "خصوص",
    "بهسختی": "به" + ZWNJ + "سختی",
    "بسختی": "به" + ZWNJ + "سختی",
    "بهجهت": "به" + ZWNJ + "جهت",
    "بجهت": "به" + ZWNJ + "جهت",
    "بهمحض": "به" + ZWNJ + "محض",
    "بمحض": "به" + ZWNJ + "محض",
    "بهموجب": "به" + ZWNJ + "موجب",
    "بموجب": "به" + ZWNJ + "موجب",
}
ZWNJ_COMPOUND_PREFIXES = ("برون", "بوم", "تک", "درون", "زیست", "میان", "نیم")
JOINED_COMPOUND_PREFIXES = tuple(sorted((
    "ابر", "ارتا", "با", "باز", "بر", "بینا", "پاد", "پرا", "پسا",
    "پیرا", "پیشا", "ترا", "چند", "در", "دگر", "رایا", "زیر",
    "فر", "فرا", "فرو", "نا", "وا", "ور",
), key=len, reverse=True))
ZWNJ_PREFIX_ATTACHED_EXAMPLES = {
    "برونمرزی": "برون" + ZWNJ + "مرزی",
    "بومشناسی": "بوم" + ZWNJ + "شناسی",
    "تکدرس": "تک" + ZWNJ + "درس",
    "درونمداری": "درون" + ZWNJ + "مداری",
    "زیستفناوری": "زیست" + ZWNJ + "فناوری",
    "میانواکه" + ZWNJ + "ای": "میان" + ZWNJ + "واکه" + ZWNJ + "ای",
    "نیمبند": "نیم" + ZWNJ + "بند",
}
HAM_PREFIX_EXCEPTIONS = {
    "هماره", "همان", "هماورد", "هماهنگ", "همایش", "همباز", "همتا",
    "همچنان", "همچنین", "همچو", "همچون", "همدل", "همدم", "همدیگر",
    "همراه", "همزن", "همسان", "همسایه", "همسر", "همشهری", "همشیره",
    "همکار", "همکرد", "همکف", "همگن", "همگون", "همو", "هموار",
    "همواره", "هموند", "همیدون", "همین",
}


class DasturkhatPreferredSpellchecker(
    unohelper.Base, XProofreader, XSupportedLocales,
    XServiceInfo, XServiceName, XServiceDisplayName
):
    SERVICE_NAME = "com.sun.star.linguistic2.Proofreader"
    IMPLEMENTATION_NAME = "org.openoffice.comp.pyuno.DasturkhatPreferred"
    DISPLAY_NAME = "دستورخط؛ رسم‌الخط مرجّح فرهنگستان"

    def __init__(self, ctx, *args):
        self.ctx = ctx
        self._ignored = set()
        self.locales = (Locale("fa", "IR", ""),)
        self.verbs = set()
        self.nominals = set()
        self.adjectives = set()
        self.numerals = set()
        self.degree_forms = set()
        self.preferred_forms = {}
        self.preferred_phrases = ()
        data_path = os.path.join(os.path.dirname(__file__), "preferred-data.json")
        try:
            with open(data_path, "r", encoding="utf-8") as source:
                data = json.load(source)
            self.verbs = set(data.get("verbs", ()))
            self.nominals = set(data.get("nominals", ()))
            self.adjectives = set(data.get("adjectives", ()))
            self.numerals = set(data.get("numerals", ()))
            self.degree_forms = set(data.get("degree_forms", ()))
        except (OSError, ValueError):
            # Keep the extension loadable if the generated data file is absent.
            pass
        forms_path = os.path.join(os.path.dirname(__file__), "preferred-spellings.json")
        try:
            with open(forms_path, "r", encoding="utf-8") as source:
                spelling_data = json.load(source)
            self.preferred_forms = spelling_data.get("forms", {})
            self.preferred_phrases = tuple(spelling_data.get("phrases", ()))
        except (OSError, ValueError):
            pass

    def getServiceName(self):
        return self.IMPLEMENTATION_NAME

    def getImplementationName(self):
        return self.IMPLEMENTATION_NAME

    def supportsService(self, service_name):
        return service_name == self.SERVICE_NAME

    def getSupportedServiceNames(self):
        return (self.SERVICE_NAME,)

    def getServiceDisplayName(self, locale):
        return self.DISPLAY_NAME

    def hasLocale(self, locale):
        return locale.Language == "fa" and locale.Country in ("", "IR")

    def getLocales(self):
        return self.locales

    def isSpellChecker(self):
        return False

    def ignoreRule(self, rule_id, locale):
        self._ignored.add(rule_id)

    def resetIgnoreRules(self):
        self._ignored.clear()

    def _make_error(self, start, length, rule_id, suggestion, comment):
        error = uno.createUnoStruct(
            "com.sun.star.linguistic2.SingleProofreadingError"
        )
        error.nErrorStart = start
        error.nErrorLength = length
        error.nErrorType = 2  # TextMarkupType.PROOFREADING
        error.aRuleIdentifier = rule_id
        error.aShortComment = comment
        error.aFullComment = comment
        error.aSuggestions = (suggestion,)
        color = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
        color.Name = "LineColor"
        color.Value = 0xE53935
        error.aProperties = (color,)
        return error

    @staticmethod
    def _degree_form(stem, suffix):
        separator = "" if stem and stem[-1] in UNJOINABLE_ENDINGS else ZWNJ
        return stem + separator + suffix

    @staticmethod
    def _normalize_spelling(word):
        normalized = unicodedata.normalize("NFKC", word)
        return NORMALIZE_MARKS_RE.sub("", normalized)

    @staticmethod
    def _single_verb_prefix_form(prefix, verb):
        if verb.startswith("ایست"):
            return prefix + verb
        if verb.startswith("آ"):
            return {"ب": "بی", "ن": "نی", "م": "می"}[prefix] + "ا" + verb[1:]
        if verb.startswith("ا"):
            return {"ب": "بی", "ن": "نی", "م": "می"}[prefix] + verb[1:]
        return prefix + verb

    def _find_errors(self, text, sentence_start, sentence_end):
        errors = []
        tokens = list(TOKEN_RE.finditer(text))

        def add(start, end, rule_id, suggestion, comment):
            if rule_id in self._ignored or not suggestion:
                return
            if start < sentence_start or end > sentence_end:
                return
            if text[start:end] == suggestion:
                return
            errors.append(self._make_error(
                start, end - start, rule_id, suggestion, comment
            ))

        # Prefixes and suffixes are checked with lexical POS data so ordinary
        # words that merely share the same ending are left alone.
        for index, token in enumerate(tokens):
            word = token.group(0)

            table_suggestion = self.preferred_forms.get(
                self._normalize_spelling(word)
            )
            if table_suggestion:
                add(token.start(), token.end(), "lilak-academy-preferred-form",
                    table_suggestion,
                    "صورتِ مرجّح در جدول واژه‌های چنداملاییِ فرهنگستان آمده است.")
                continue

            lexical_roots = self.nominals | self.adjectives

            # Productive suffixes which the Academy writes with a ZWNJ,
            # except after letters that cannot connect to the following letter.
            for suffix in ZWNJ_SUFFIXES:
                if word.endswith(ZWNJ + suffix):
                    stem = word[:-len(ZWNJ + suffix)]
                    joined = stem + suffix
                    if suffix == "وار" and joined in WAR_SUFFIX_EXCEPTIONS:
                        suggestion = joined
                    elif suffix == "سان" and joined in SAN_SUFFIX_EXCEPTIONS:
                        suggestion = joined
                    else:
                        suggestion = self._degree_form(stem, suffix)
                    if stem in lexical_roots and suggestion != word:
                        add(token.start(), token.end(), "lilak-productive-suffix",
                            suggestion,
                            "این پسوند با جداکنندهٔ مقرر نوشته می‌شود.")
                    break
                elif word.endswith(suffix):
                    stem = word[:-len(suffix)]
                    if (stem in lexical_roots
                            and word not in WAR_SUFFIX_EXCEPTIONS
                            and word not in SAN_SUFFIX_EXCEPTIONS):
                        suggestion = self._degree_form(stem, suffix)
                        if suggestion != word:
                            add(token.start(), token.end(), "lilak-productive-suffix",
                                suggestion,
                                "این پسوند با جداکنندهٔ مقرر نوشته می‌شود.")
                    break

            # "-گر/-گری" take a ZWNJ after ط/ظ and in a few
            # explicitly listed difficult-to-read forms. The book's
            # pronounced/non-pronounced final-he distinction is not guessed.
            for suffix in CONDITIONAL_ZWNJ_SUFFIXES:
                if word.endswith(ZWNJ + suffix):
                    stem = word[:-len(ZWNJ + suffix)]
                    needs_zwnj = (stem in CONDITIONAL_ZWNJ_ROOTS
                                  or (stem and stem[-1] in {"ط", "ظ"}))
                    if needs_zwnj and stem in lexical_roots:
                        continue
                    if (stem in lexical_roots and stem
                            and stem[-1] not in {"ه", "ی", "ط", "ظ"}):
                        add(token.start(), token.end(), "lilak-ger-suffix",
                            stem + suffix,
                            "پسوند «گر/گری» در این صورت پیوسته نوشته می‌شود.")
                    break
                elif word.endswith(suffix):
                    stem = word[:-len(suffix)]
                    needs_zwnj = (stem in CONDITIONAL_ZWNJ_ROOTS
                                  or (stem and stem[-1] in {"ط", "ظ"}))
                    if needs_zwnj and stem in lexical_roots:
                        add(token.start(), token.end(), "lilak-ger-suffix",
                            stem + ZWNJ + suffix,
                            "پسوند «گر/گری» در این صورت با نیم‌فاصله نوشته می‌شود.")
                    break

            # The productive suffixoids "-خانه/-نامه" take a ZWNJ,
            # except for the lexicalized joined forms named by the Academy.
            for suffix in ("خانه", "نامه"):
                if word.endswith(ZWNJ + suffix):
                    stem = word[:-len(ZWNJ + suffix)]
                    joined = stem + suffix
                    if joined in JOINED_LEXICALIZED_SUFFIX_EXCEPTIONS:
                        add(token.start(), token.end(), "lilak-house-name-suffix",
                            joined,
                            "این واژه از استثناهای پیوسته‌نویسیِ «خانه/نامه» است.")
                    break
                elif word.endswith(suffix):
                    stem = word[:-len(suffix)]
                    if (stem in lexical_roots
                            and word not in JOINED_LEXICALIZED_SUFFIX_EXCEPTIONS):
                        add(token.start(), token.end(), "lilak-house-name-suffix",
                            stem + ZWNJ + suffix,
                            "پسوندوارهٔ «خانه/نامه» با نیم‌فاصله نوشته می‌شود.")
                    break

            # Numerals take a ZWNJ before "-گانه"; the connective-letter
            # exception is handled by _degree_form.
            if word.endswith(ZWNJ + "گانه"):
                stem = word[:-len(ZWNJ + "گانه")]
                if stem in self.numerals:
                    suggestion = self._degree_form(stem, "گانه")
                    if suggestion != word:
                        add(token.start(), token.end(), "lilak-numeral-gane",
                            suggestion, "پسوند «گانه» پس از عدد جدا نوشته می‌شود.")
            elif word.endswith("گانه"):
                stem = word[:-len("گانه")]
                if stem in self.numerals:
                    add(token.start(), token.end(), "lilak-numeral-gane",
                        self._degree_form(stem, "گانه"),
                        "پسوند «گانه» پس از عدد جدا نوشته می‌شود.")

            # The ordinal forms of "سی" use a ZWNJ.
            for suffix in ("امین", "امی", "ام"):
                if word.endswith(suffix) and word[:-len(suffix)] == "سی":
                    add(token.start(), token.end(), "lilak-thirty-ordinal",
                        "سی" + ZWNJ + suffix,
                        "صورت‌های ترتیبیِ ساخته‌شده با «سی» نیم‌فاصله می‌گیرند.")
                    break

            # The suffix "-واره" is written attached.
            for suffix in ATTACHED_SUFFIXES:
                if word.endswith(ZWNJ + suffix):
                    stem = word[:-len(ZWNJ + suffix)]
                    if stem in lexical_roots:
                        add(token.start(), token.end(), "lilak-attached-suffix",
                            stem + suffix,
                            "پسوند «واره» پیوسته نوشته می‌شود.")
                    break

            for suffix in DEGREE_SUFFIXES:
                if word.endswith(ZWNJ + suffix):
                    stem = word[:-len(ZWNJ + suffix)]
                    if stem in self.adjectives:
                        add(token.start(), token.end(), "lilak-degree-suffix",
                            self._degree_form(stem, suffix),
                            "پسوند تفضیلی/عالی با جداکنندهٔ درست نوشته می‌شود.")
                        break
                elif word.endswith(suffix):
                    stem = word[:-len(suffix)]
                    if (stem in self.adjectives
                            and word not in self.degree_forms
                            and word not in DEGREE_EXCEPTIONS):
                        add(token.start(), token.end(), "lilak-degree-suffix",
                            self._degree_form(stem, suffix),
                            "پسوند تفضیلی/عالی با جداکنندهٔ درست نوشته می‌شود.")
                        break

            # "این/آن" are normally separate from the following lexical word.
            # Split an attached form only when its second element is known and
            # the whole token is not one of the Academy's lexicalized exceptions.
            demonstrative_exceptions = {
                "اینجا", "آنجا", "آنچه", "آنکه", "اینکه", "وانگهی",
                "اینطور", "آنطور", "اینگونه", "آنگونه",
            }
            if word not in demonstrative_exceptions:
                for demonstrative in ("این", "آن"):
                    if word.startswith(demonstrative) and len(word) > len(demonstrative):
                        rest = word[len(demonstrative):]
                        if rest.startswith(ZWNJ):
                            rest = rest[len(ZWNJ):]
                        if rest in self.nominals | self.adjectives:
                            add(token.start(), token.end(),
                                "lilak-demonstrative-space",
                                demonstrative + " " + rest,
                                "«این/آن» پیش از این واژه با فاصلهٔ کامل نوشته می‌شود.")
                        break

            # "چه" is separate from its following word except in the fixed
            # lexicalized forms enumerated by the Academy.
            if word.startswith("چه") and len(word) > 2:
                rest = word[2:]
                if rest.startswith(ZWNJ):
                    rest = rest[len(ZWNJ):]
                if (rest in self.nominals | self.adjectives | self.numerals
                        and word not in {"چرا", "چطور", "چقدر", "چگونه"}):
                    add(token.start(), token.end(), "lilak-che-space",
                        "چه " + rest,
                        "«چه» در این ساخت با فاصلهٔ کامل نوشته می‌شود.")

            # The postposition "را" is separate from a known nominal. Do not
            # split lexicalized exceptions such as "مرا" or the adverb "چرا".
            if word.endswith("را") and word not in {"چرا", "مرا"}:
                stem = word[:-2]
                if stem in self.nominals and word not in self.nominals:
                    add(token.start(), token.end(), "lilak-ra-space",
                        stem + " را",
                        "نشانهٔ مفعولی «را» با فاصلهٔ کامل نوشته می‌شود.")

            attached_suggestion = DEMONSTRATIVE_ATTACHED_FORMS.get(word)
            if attached_suggestion:
                add(token.start(), token.end(), "lilak-demonstrative-compound",
                    attached_suggestion,
                    "این ترکیب با نیم‌فاصله نوشته می‌شود.")

            same_suggestion = SAME_FORMS_ATTACHED.get(word)
            if same_suggestion:
                add(token.start(), token.end(), "lilak-same-demonstrative",
                    same_suggestion,
                    "این ترکیب با نیم‌فاصله نوشته می‌شود.")

            # Repair common attached forms of prefixes that the Academy
            # writes with a ZWNJ, then generalize only when the base is known
            # and the whole attached token is not an independent dictionary word.
            prefix_suggestion = ZWNJ_PREFIX_ATTACHED_EXAMPLES.get(word)
            if prefix_suggestion:
                add(token.start(), token.end(), "lilak-compound-prefix",
                    prefix_suggestion,
                    "این پیشوندواره با نیم‌فاصله نوشته می‌شود.")
            else:
                lexical_roots = self.nominals | self.adjectives
                for compound_prefix in ZWNJ_COMPOUND_PREFIXES:
                    if not word.startswith(compound_prefix):
                        continue
                    rest = word[len(compound_prefix):]
                    if not rest or rest[0] == ZWNJ:
                        break
                    base = rest.split(ZWNJ, 1)[0]
                    if word not in lexical_roots and base in lexical_roots:
                        add(token.start(), token.end(), "lilak-compound-prefix",
                            compound_prefix + ZWNJ + rest,
                            "این پیشوندواره با نیم‌فاصله نوشته می‌شود.")
                    break

            # These prefixes cannot connect to the next word in the standard
            # spelling, so a ZWNJ after them is removed when the base is known.
            for compound_prefix in JOINED_COMPOUND_PREFIXES:
                marker = compound_prefix + ZWNJ
                if word.startswith(marker):
                    rest = word[len(marker):]
                    base = rest.split(ZWNJ, 1)[0]
                    if base and base in (lexical_roots | self.verbs):
                        add(token.start(), token.end(), "lilak-joined-prefix",
                            compound_prefix + rest,
                            "این پیشوند در این ترکیب پیوسته نوشته می‌شود.")
                    break

            # Negative prefix "بیـ" uses ZWNJ. Skip lexicalized exceptions,
            # names, and verb forms that only resemble this prefix.
            be_example = BE_HALFSPACE_ATTACHED_FORMS.get(word)
            if be_example:
                add(token.start(), token.end(), "lilak-be-prefix", be_example,
                    "این ترکیبِ ساخته‌شده با «به» با نیم‌فاصله نوشته می‌شود.")

            bi_example = BI_PREFIX_ATTACHED_EXAMPLES.get(word)
            if bi_example:
                add(token.start(), token.end(), "lilak-bi-prefix", bi_example,
                    "پیشوند نفیِ «بی» با نیم‌فاصله نوشته می‌شود.")
            elif word.startswith("بی") and len(word) > 2 and word[2] != ZWNJ:
                if word not in self.verbs:
                    is_exception = any(word.startswith(item) for item in BI_PREFIX_EXCEPTIONS)
                    rest = word[2:]
                    lexical_roots = self.nominals | self.adjectives
                    if not is_exception and rest in lexical_roots:
                        add(token.start(), token.end(), "lilak-bi-prefix",
                            "بی" + ZWNJ + rest,
                            "پیشوند نفیِ «بی» با نیم‌فاصله نوشته می‌شود.")

            # Productive "همـ" compounds use ZWNJ; lexicalized exceptions
            # listed by the Academy stay joined. Only attached inputs are checked,
            # since a full space can mean the adverb "also" plus a noun.
            if (word.startswith("هم") and not word.startswith("همی")
                    and len(word) > 2 and word[2] != ZWNJ
                    and not any(word.startswith(item) for item in HAM_PREFIX_EXCEPTIONS)):
                rest = word[2:]
                base = rest.split(ZWNJ, 1)[0]
                lexical_roots = self.nominals | self.adjectives
                root_known = base in lexical_roots
                if not root_known:
                    for suffix in HA_SUFFIXES:
                        if base.endswith(suffix) and base[:-len(suffix)] in lexical_roots:
                            root_known = True
                            break
                if root_known:
                    add(token.start(), token.end(), "lilak-ham-prefix",
                        "هم" + ZWNJ + rest,
                        "پیشوند «هم» در این ترکیب با نیم‌فاصله نوشته می‌شود.")

            # The book treats these lexicalized forms of "هر" as one word.
            normalized_hare = word.replace(ZWNJ, "")
            if ZWNJ in word and normalized_hare in HARE_COMPOUND_FORMS:
                add(token.start(), token.end(), "lilak-har-compound",
                    normalized_hare,
                    "این صورتِ واژگانی‌شده با «هر» پیوسته نوشته می‌شود.")

            # These five lexicalized compounds take a ZWNJ after "هیچ".
            normalized_hich = "هیچ" + ZWNJ + word.replace("هیچ", "", 1).replace(ZWNJ, "")
            if word.startswith("هیچ") and normalized_hich in HIC_COMPOUND_FORMS:
                add(token.start(), token.end(), "lilak-hich-compound",
                    normalized_hich,
                    "این ترکیبِ واژگانی‌شده با «هیچ» با نیم‌فاصله نوشته می‌شود.")

            for prefix in MI_PREFIXES:
                if word.startswith(prefix) and ZWNJ not in word:
                    stem = word[len(prefix):]
                    if stem and stem in self.verbs:
                        add(token.start(), token.end(), "lilak-mi-prefix",
                            prefix + ZWNJ + stem,
                            "پیشوند فعلی با نیم‌فاصله نوشته می‌شود.")
                        break

            if index + 1 < len(tokens):
                next_token = tokens[index + 1]
                next_word = next_token.group(0)
                gap = text[token.end():next_token.start()]

                if gap and gap.isspace() and word in {"این", "آن"}:
                    if next_word in DEMONSTRATIVE_PARTS:
                        add(token.start(), next_token.end(),
                            "lilak-demonstrative-compound",
                            word + ZWNJ + next_word,
                            "این ترکیب با نیم‌فاصله نوشته می‌شود.")

                if gap and gap.isspace() and word in {"ب", "ن", "م"}:
                    suggestion = SINGLE_VERB_PREFIX_EXAMPLES.get((word, next_word))
                    if not suggestion and next_word in self.verbs:
                        suggestion = self._single_verb_prefix_form(word, next_word)
                    if suggestion:
                        add(token.start(), next_token.end(), "lilak-be-verb-prefix",
                            suggestion,
                            "این پیشوند فعلی به فعل می‌چسبد و گاهی شکل آغاز فعل را تغییر می‌دهد.")

                if gap and gap.isspace() and word == "سی" and next_word in {"ام", "امی", "امین"}:
                    add(token.start(), next_token.end(), "lilak-thirty-ordinal",
                        "سی" + ZWNJ + next_word,
                        "صورت‌های ترتیبیِ ساخته‌شده با «سی» نیم‌فاصله می‌گیرند.")

                if gap and gap.isspace() and word == "بی":
                    if next_word in BI_PREFIX_SPACE_BASES:
                        add(token.start(), next_token.end(), "lilak-bi-prefix",
                            "بی" + ZWNJ + next_word,
                            "پیشوند نفیِ «بی» با نیم‌فاصله نوشته می‌شود.")

                if gap and gap.isspace() and word == "هر":
                    if next_word in HARE_COMPOUND_STEMS:
                        add(token.start(), next_token.end(),
                            "lilak-har-compound",
                            "هر" + next_word,
                            "این صورتِ واژگانی‌شده با «هر» پیوسته نوشته می‌شود.")

                if gap and gap.isspace() and word == "هیچ":
                    if next_word in HIC_COMPOUND_STEMS:
                        add(token.start(), next_token.end(),
                            "lilak-hich-compound",
                            "هیچ" + ZWNJ + next_word,
                            "این ترکیبِ واژگانی‌شده با «هیچ» با نیم‌فاصله نوشته می‌شود.")

                if gap and gap.isspace() and next_word in {"تر", "ترین"}:
                    if (word in self.adjectives
                            and word + next_word not in self.degree_forms
                            and word + next_word not in DEGREE_EXCEPTIONS):
                        add(token.start(), next_token.end(),
                            "lilak-degree-suffix",
                            self._degree_form(word, next_word),
                            "پسوند تفضیلی/عالی با جداکنندهٔ درست نوشته می‌شود.")

                if gap and gap.isspace() and word in MI_PREFIXES:
                    verb = next_word
                    if verb in self.verbs and not (
                        word == "همی" and verb in EMPHATIC_HAMI_FOLLOWING
                    ):
                        add(token.start(), next_token.end(),
                            "lilak-mi-prefix",
                            word + ZWNJ + verb,
                            "پیشوند فعلی با نیم‌فاصله نوشته می‌شود.")

                if gap and gap.isspace() and next_word == "ها":
                    if word in self.nominals:
                        add(token.start(), next_token.end(),
                            "lilak-plural-ha",
                            word + ZWNJ + "ها",
                            "صورتِ دارای نیم‌فاصله برای پسوند «ها» مرجّح است.")

            # Catch attached but unseparated forms such as کتابها and کتابهایش.
            if ZWNJ not in word:
                for suffix in HA_SUFFIXES:
                    if word.endswith(suffix):
                        stem = word[:-len(suffix)]
                        if stem and stem in self.nominals:
                            add(token.start(), token.end(),
                                "lilak-plural-ha",
                                stem + ZWNJ + suffix,
                                "صورتِ دارای نیم‌فاصله برای پسوند «ها» مرجّح است.")
                            break

        # Some fixed expressions are written as one word or with half-spaces.
        # Match only the exact listed sequence of whitespace-separated tokens;
        # punctuation and unrelated words prevent a match.
        phrase_ranges = []
        for phrase in self.preferred_phrases:
            parts = phrase.get("parts", ())
            preferred = phrase.get("preferred", "")
            if not parts or not preferred or len(tokens) < len(parts):
                continue
            normalized_parts = tuple(self._normalize_spelling(part) for part in parts)
            for first in range(len(tokens) - len(parts) + 1):
                matched = True
                for offset, part in enumerate(normalized_parts):
                    current = tokens[first + offset]
                    if self._normalize_spelling(current.group(0)) != part:
                        matched = False
                        break
                    if offset:
                        previous = tokens[first + offset - 1]
                        gap = text[previous.end():current.start()]
                        if not gap or not gap.isspace():
                            matched = False
                            break
                if not matched:
                    continue
                start = tokens[first].start()
                end = tokens[first + len(parts) - 1].end()
                if start < sentence_start or end > sentence_end:
                    continue
                if text[start:end] == preferred:
                    continue
                phrase_ranges.append((start, end))
                errors.append(self._make_error(
                    start, end - start, "lilak-academy-preferred-phrase",
                    preferred,
                    "صورتِ مرجّحِ این ترکیب در دستور خط فرهنگستان آمده است."
                ))

        if phrase_ranges:
            errors = [error for error in errors if not any(
                error.nErrorStart < end
                and error.nErrorStart + error.nErrorLength > start
                and error.aRuleIdentifier != "lilak-academy-preferred-phrase"
                for start, end in phrase_ranges
            )]
        errors.sort(key=lambda error: error.nErrorStart)
        return tuple(errors)

    def doProofreading(
        self, document_id, text, locale, start_of_sentence,
        suggested_sentence_end, properties
    ):
        result = uno.createUnoStruct(
            "com.sun.star.linguistic2.ProofreadingResult"
        )
        result.aDocumentIdentifier = document_id
        result.aText = text
        result.aLocale = locale
        result.nStartOfSentencePosition = start_of_sentence
        end = min(max(suggested_sentence_end, start_of_sentence), len(text))
        next_sentence = end
        while next_sentence < len(text) and text[next_sentence] == " ":
            next_sentence += 1
        if next_sentence == suggested_sentence_end and next_sentence < len(text):
            next_sentence += 1
        result.nStartOfNextSentencePosition = next_sentence
        result.nBehindEndOfSentencePosition = next_sentence
        result.aProperties = ()
        result.xProofreader = self
        result.aErrors = ()

        if not self.hasLocale(locale) or not text:
            return result

        result.aErrors = self._find_errors(
            text, start_of_sentence, next_sentence
        )
        return result


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    DasturkhatPreferredSpellchecker,
    DasturkhatPreferredSpellchecker.IMPLEMENTATION_NAME,
    (DasturkhatPreferredSpellchecker.SERVICE_NAME,),
)

