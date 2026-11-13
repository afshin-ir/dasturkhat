# Dastoorkhat — Persian Spell Checking and Preferred Orthography

[![صفحهٔ فارسی افزونهٔ دستورخط](assets/readme-fa-button.png)](README.fa.md)

Dastoorkhat provides an optional LibreOffice Writer extension for checking Academy-preferred Persian spellings, alongside its Persian Hunspell dictionary. This project continues Afshin Falatouni’s fork of the upstream Lilak dictionary, which supplies the morphological data and Hunspell spell-checking foundation.

## Academy-preferred orthography in LibreOffice Writer

Version **3.16** adds a separate, offline proofreader for LibreOffice Writer. It works alongside Hunspell: Hunspell checks whether words are spelled correctly, while the Dastoorkhat proofreader flags selected departures from the preferred spellings in the second edition of the Academy of Persian Language and Literature's *Dastur-e Khat-e Farsi*.

The Writer extension uses the grammar-checking interface to underline a flagged form and offer a replacement. Its current rules include:

- **Verb prefixes:** checks attached and separated forms of *mi*, *nemi*, and *hami* with known verbs. It also handles the verb prefixes *b*, *n*, and *m*, including listed spelling changes before verbs beginning with alef or alef-madda.
- **Plural suffix *-ha*:** recommends the half-space spelling for recognized nouns, including listed examples involving foreign words, proper names, silent *h*, and long stems.
- **Lexicalized compounds:** checks listed forms with *har*, *hich*, *hamin/haman*, and *in/an + tor/gune*.
- **Question words and the object marker *ra*:** repairs selected attached forms when the following or preceding lexical base is known.
- **Productive affixes:** checks *-tar/-tarin*, *-var*, *-san*, *-asa*, *-agin*, *-bare*, *-jat*, *-fam*, *-vesh*, *-gar/-gari*, *-vare*, *-khane/-name*, and numeral suffix *-gane*, using lexical data and listed exceptions.
- **Prefixes and compound words:** checks listed attached and half-spaced prefixes, plus selected repeated, coordinated, descriptive, proper-name, and multiword compounds.
- **Preferred word forms:** includes **212 direct replacements** drawn from the book's general-word and proper-name spelling tables and its explicit examples.
- **Multiword expressions:** includes **110 phrase patterns** for selected compound prepositions, conjunctions, and other examples. A phrase is matched only when its listed parts occur consecutively with full spaces between them.

The data is stored in [`src/data/preferred-spellings.json`](src/data/preferred-spellings.json). The full rule-by-rule scope and limitations are documented in the [Persian orthography report](REPORT_dastur-khat-fa.md).

### Scope and limitations

This is a spelling and orthography checker, not a grammar or meaning analyzer. It cannot reliably resolve context-sensitive choices such as the roles of *in/an*, *che*, *ra*, or *ke* in every sentence. Ambiguous table entries, historical spellings, and open-ended Arabic expressions are not all converted automatically. The extension checks only rules and examples that can be recognized safely from the token and available lexical data.

### Enable it in Writer

Install the `.oxt` extension, then open **Tools → Options → Languages and Locales → Writing Aids**. Enable **Check spelling as you type** and **Check grammar as you type**, and set the text language to Persian. Hunspell remains responsible for ordinary spell checking; the Dastoorkhat proofreader supplies these preferred-orthography checks separately.

### Build the LibreOffice extension

With Python 3 and the repository data available, run:

```bash
make libreoffice
```

The package is written to `build/dastoorkhat-fa-IR.oxt`. The repository's GitHub Actions workflow builds this package on pushes to the orthography branch.

## Build the Hunspell dictionary

Run the following commands from the repository root:

```bash
make build
make test
```

The generated `.dic` and `.aff` files are written to `build/`. The source lexicon is in `src/data/lexicon`; it contains Persian words with part-of-speech tags and other morphological information.

## Use the Hunspell dictionary

- The upstream Lilak Hunspell dictionary is available from [Lilak releases](https://github.com/b00f/lilak/releases/).
- In Firefox, install the upstream [Lilak Persian Dictionary](https://addons.mozilla.org/en-US/firefox/addon/lilak-persian-dictionary/).
- In Chrome, add Persian under language settings and enable spell checking.

## Contribute

Useful contributions include Persian words with accurate part-of-speech and morphological tags. See `src/data/lexicon` for the lexicon format. Please report dictionary or rule issues in the repository's issue tracker.

## Project history and license

Dastoorkhat is an open-source project inspired by the title of the Academy of Persian Language and Literature’s book *Dastur-e Khat-e Farsi*. It continues the Persian morphology work of the upstream Lilak project and honors Abolhassan Najafi, an associate member of the Academy and author of *Ghalat Nanevisim*.

Dastoorkhat is distributed under the Apache License 2.0. See [`LICENSE`](LICENSE) for the full license text.

Special thanks to Dr. Hamid Farrroukh, Dr. Hamid Hassani, Dr. Reza Moshksar, and 5j9 for their work on Persian language resources.
