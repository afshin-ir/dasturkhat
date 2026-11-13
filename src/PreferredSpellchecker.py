# -*- coding: utf-8 -*-
"""Academy-preferred Persian spelling checks for LibreOffice Writer."""

import json
import os
import re

import uno
import unohelper
from com.sun.star.lang import Locale, XServiceInfo, XServiceName, XServiceDisplayName
from com.sun.star.linguistic2 import XProofreader, XSupportedLocales


ZWNJ = "\u200c"
TOKEN_RE = re.compile(r"[\w\u200c]+", re.UNICODE)
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
ZWNJ_COMPOUND_PREFIXES = ("برون", "بوم", "تک", "درون", "زیست", "میان", "نیم")
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


class LilakPreferredSpellchecker(
    unohelper.Base, XProofreader, XSupportedLocales,
    XServiceInfo, XServiceName, XServiceDisplayName
):
    SERVICE_NAME = "com.sun.star.linguistic2.Proofreader"
    IMPLEMENTATION_NAME = "org.openoffice.comp.pyuno.LilakPreferred"
    DISPLAY_NAME = "لیلک؛ رسم‌الخط مرجّح فرهنگستان"

    def __init__(self, ctx, *args):
        self.ctx = ctx
        self._ignored = set()
        self.locales = (Locale("fa", "IR", ""),)
        self.verbs = set()
        self.nominals = set()
        self.adjectives = set()
        self.degree_forms = set()
        data_path = os.path.join(os.path.dirname(__file__), "preferred-data.json")
        try:
            with open(data_path, "r", encoding="utf-8") as source:
                data = json.load(source)
            self.verbs = set(data.get("verbs", ()))
            self.nominals = set(data.get("nominals", ()))
            self.adjectives = set(data.get("adjectives", ()))
            self.degree_forms = set(data.get("degree_forms", ()))
        except (OSError, ValueError):
            # Keep the extension loadable if the generated data file is absent.
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
    LilakPreferredSpellchecker,
    LilakPreferredSpellchecker.IMPLEMENTATION_NAME,
    (LilakPreferredSpellchecker.SERVICE_NAME,),
)
