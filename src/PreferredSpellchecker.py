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
        data_path = os.path.join(os.path.dirname(__file__), "preferred-data.json")
        try:
            with open(data_path, "r", encoding="utf-8") as source:
                data = json.load(source)
            self.verbs = set(data.get("verbs", ()))
            self.nominals = set(data.get("nominals", ()))
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

        # Prefixes are part of verbs. A separate Hunspell word check cannot
        # distinguish "می شود" from two individually valid words.
        for index, token in enumerate(tokens):
            word = token.group(0)

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
                gap = text[token.end():next_token.start()]
                if gap and gap.isspace() and word in MI_PREFIXES:
                    verb = next_token.group(0)
                    if verb in self.verbs and not (
                        word == "همی" and verb in EMPHATIC_HAMI_FOLLOWING
                    ):
                        prefix = word
                        add(token.start(), next_token.end(),
                            "lilak-mi-prefix",
                            prefix + ZWNJ + verb,
                            "پیشوند فعلی با نیم‌فاصله نوشته می‌شود.")

                if gap and gap.isspace() and next_token.group(0) == "ها":
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
        result.nStartOfNextSentencePosition = end
        result.nBehindEndOfSentencePosition = end
        result.aProperties = ()
        result.xProofreader = self
        result.aErrors = ()

        if not self.hasLocale(locale) or not text:
            return result

        result.aErrors = self._find_errors(text, start_of_sentence, end)
        return result


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    LilakPreferredSpellchecker,
    LilakPreferredSpellchecker.IMPLEMENTATION_NAME,
    (LilakPreferredSpellchecker.SERVICE_NAME,),
)
