# Lilak, Persian Spell Checking Dictionary
  [![Build Status](https://travis-ci.com/b00f/lilak.svg?branch=master)](https://travis-ci.com/b00f/lilak)
  [![Donate](https://img.shields.io/badge/support-patreon-F96854.svg?style=flat-square)](https://patreon.com/b00f)

[Lilak](https://github.com/b00f/lilak) is an open source project for generating Persian dictionary for [hunspell](https://github.com/hunspell/hunspell) spell checker based on Persian Morphology.

In Persian language affixes can change the meaning of the word. Some suffixes attached to a word as short form of verbs. Part-of-speech plays an important role in Persian language. In some cases the pronunciation of the word can change the suffixes. Check the code for more information.

Lilak has a [lexicon](http://lilak-project.com) of Persian words with part-of-speech tags. Lilak builds a dictionary for hunspell to predict the best form of compound words based on morphological rules.

## Content

```text
lilak
  |-- build           : Build folder. Compiled dictionary goes here.
  |
  |-- src
  |   |-- data
  |   |   |-- lexicon       : Lexicon of Persian words with part-of-speech tags
  |   |   |-- affixes       : Affix (prefix or suffix) rules
  |   |   |-- dic_users     : List of words without POS tag.
  |   |   \-- verbs.htm     : List of Persian verbs (unstemmed)
  |   |
  |   |-- lilak.py    : Python script for building lilak dictionary
  |   \-- test.py     : Python script to test lilak accuracy
  |
  |-- test
  |   |-- text1       : "Farsi(Persian) is Sugar", A short story by Mohammad-Ali Jamalzadeh
  |   |-- text2       : "A Hekayat" By Saadi
  |   |-- text3       : "A Ghazal" By Hafez
  |   |-- text4       : "Yazdgerd Kingdom" By Ferdowsi
  |   |-- text5       : "A Ghazal" By Muhammad Husayn Tabataba'i
  |   |-- text6       : "Have a Safe Trip" A poem by Shafii Kadkani
  |   |-- text7       : "Se Tar" A short story by Jalal Al-e-Ahmad
  |   |-- text8       : "End of Shahname" By Mehdi Akhavan-Sales
  |   |-- text9       : "The Water"s Footsteps" By Sohrab Sepehri
  |   |-- text10      : "Nei Name" By Rumi
  |   \-- verbs       : Some inflected verbs
  |
  |-- README.md       :
  \-- LICENCE         : License file
```

## Building Dictionary

Before using lilak please make sure you have install python 3.x.

To build the lilak dictionary, run lilak.py from `src` folder:

```bash
make build
make test
```

You can find the compiled dictionary at the `build` folder.

check [result.log](./test/result.log) for test result.

## How to contribute

The best way you can contribute on this project is collecting words with correct part-of-speech tags.
Part-of-speech is important to build Lilak. It should classified in main types like: verb, noun, adjective, etc. Also some other tags will be useful. like tense of verb, singular or plural, etc.
Check the `src/data/lexicon` for more information

Please open an issue if you find any mistakes while using lilak.

## Using Lilak

- You can find compiled dictionaries [here](https://github.com/b00f/lilak/releases/).
- Mozilla Firefox: Install lilak extension from here [here](https://addons.mozilla.org/en-US/firefox/addon/lilak-persian-dictionary/).
- Google Chrome: Go to Settings, find Language and input settings, add Persian language and make sure you have enabled the spell checker option.

## Supporting Lilak
If you like this project, please [donate](http://lilak-project.com/donate.php) or consider becoming a patron:

[![Become a patron](https://c5.patreon.com/external/logo/become_a_patron_button.png)](https://patreon.com/b00f)

## License
Lilak is published under Apache licence. You may freely use, reproduce, modify or distribute it. If you think lilak is useful please support it.

## About the Name

*lilac* in English came from French lilac "shrub of genus Syringa with mauve flowers"
from Spanish lilac, from Arabic *lilak*, from Persian *lilak*, variant of nilak "bluish"

## In Memory of Abolhassan Najafi

[Abolhassan Najafi](https://en.wikipedia.org/wiki/Abolhassan_Najafi) was an associate member of Iran's Academy of Persian Language and Literature. His most famous books is "Ghalat Nanevisim" (Let’s not write incorrect).


## Thanks

Special thanks to

- Dr. Hamid Farrroukh : [alefbaye2om](http://alefbaye2om.org/)
- Dr. Hamid Hassani : [wikipedia](https://en.wikipedia.org/wiki/Hamid_Hassani)
- Dr. Reza Moshksar : [github](https://github.com/reza1615)
- 5j9 : [github](https://github.com/5j9)


## بررسی رسم‌الخط مرجّح در LibreOffice Writer

این شاخه یک افزونهٔ جداگانهٔ بررسی رسم‌الخط فارسی برای Writer فراهم می‌کند. این بخش در کنار بررسی املای Hunspell کار می‌کند و برای خطاهای زیر زیرخط قرمز و پیشنهاد اصلاح نشان می‌دهد:

- پیشوندهای فعلی «می»، «نمی» و «همی» در صورت‌های فعلیِ شناخته‌شده: نیم‌فاصله لازم است؛ «همی نیست» به‌عنوان کاربرد تأکیدی مستثناست.
- پسوند جمع «ها» در واژه‌های اسمیِ شناخته‌شده: صورت نیم‌فاصله‌دار به‌عنوان صورت مرجّح پیشنهاد می‌شود.
- ترکیب‌های «این‌طور»، «آن‌طور»، «این‌گونه» و «آن‌گونه»: صورت چسبیده یا جدا با فاصلهٔ کامل اصلاح می‌شود.
- ترکیب‌های واژگانی‌شده با «هر»: صورت‌های «هرآینه، هرازگاهی، هرچند، هرطور، هرکدام، هرکس، هرکه، هرگاه، هرگونه، هریک» پیوسته نوشته می‌شوند.
- ترکیب‌های واژگانی‌شده با «هیچ»: «هیچ‌کدام، هیچ‌کس، هیچ‌گاه، هیچ‌گونه، هیچ‌یک» با نیم‌فاصله نوشته می‌شوند.
- پسوندهای تفضیلی و عالی «تر/ترین» برای پایه‌هایی که در واژه‌نامهٔ لیلک صفت شناخته شده‌اند: جدانویسی نادرست اصلاح می‌شود و نیم‌فاصله یا پیوستگیِ لازم پس از حروفِ ناپیوسته پیشنهاد می‌شود. صورت‌های استثناییِ «بهتر، کهتر، مهتر، بیشتر، کمتر، کلانتر» دست‌نخورده می‌مانند.

\n- صورت‌های چسبیدهٔ «همان/همین‌جا»، «همان/همین‌جور» و «همان/همین‌گونه»: نیم‌فاصله پیشنهاد می‌شود. صورت‌های جدا با فاصله کامل به‌دلیل وابستگی به بافت جمله خودکار اصلاح نمی‌شوند.\n\n
- پیشوند «همـ» در صورت‌های چسبیده‌ای که پایهٔ آن در واژه‌نامه اسم یا صفت شناخته‌شده است، به نیم‌فاصله اصلاح می‌شود؛ استثناهای پیوستهٔ برشمرده‌شده در کتاب حفظ می‌شوند. صورت‌های جدا با فاصلهٔ کامل بررسی نمی‌شوند، چون ممکن است «هم» به معنی «نیز» باشد.


- صورت‌های چسبیدهٔ نمونهٔ پیشوندواره‌های «برون، بوم، تک، درون، زیست، میان، نیم» به شکل نیم‌فاصله‌دار اصلاح می‌شوند. برای دیگر واژه‌ها، این قاعده فقط وقتی اعمال می‌شود که پایه در واژه‌نامه شناخته شده باشد و خود واژه صورت مستقلِ ثبت‌شده‌ای نباشد.


- پیشوند نفی «بی» در واژه‌های چسبیده، اگر پایه در واژه‌نامه اسم یا صفت شناخته‌شده باشد، با نیم‌فاصله پیشنهاد می‌شود؛ استثناهای واژگانی و فعل‌های هم‌شکل کنار گذاشته شده‌اند. چند نمونهٔ متن کتاب و صورت‌های جدا با فاصلهٔ کاملِ شناخته‌شده نیز اصلاح می‌شوند. عبارت‌هایی مانند «بی هیچ» به‌دلیل نقش حرف اضافه خودکار تغییر نمی‌کنند.


- ترکیب‌های صفتی و قیدیِ نمونهٔ «به‌خصوص، به‌سختی، به‌جهت، به‌محض، به‌موجب» در صورت چسبیده اصلاح می‌شوند. همچنین اگر پیشوند فعلیِ «ب/ن/م» جدا از فعلِ شناخته‌شده نوشته شود، به فعل می‌چسبد و در نمونه‌های آغازشونده با الف شکل درستِ فعل پیشنهاد می‌شود؛ مانند «ب انجامد» ← «بینجامد» و «ن افتاد» ← «نیفتاد».


- پسوندهای «ـوار، ـسان، ـآسا، ـآگین، ـباره، ـجات، ـفام، ـوش» برای پایه‌های شناخته‌شده با جداکنندهٔ مناسب پیشنهاد می‌شوند؛ استثناهای واژگانیِ «ـوار» و «ـسان» رعایت شده‌اند. صورت‌های نیم‌فاصله‌دارِ «ـواره» به شکل پیوسته اصلاح می‌شوند.


- پسوندهای «ـگر/ـگری» پس از «ط/ظ» و در نمونه‌های روشنِ «توجیه‌گر، افراط‌گری، لاابالی‌گری» نیم‌فاصله می‌گیرند. در پایان‌های «ه» و «ی» که تشخیصشان وابسته به تلفظ یا دشوارخوانی است، قاعده حدس نمی‌زند.


- پسوندواره‌های «ـخانه/ـنامه» برای پایه‌های شناخته‌شده نیم‌فاصله می‌گیرند؛ استثناهای پیوستهٔ کتاب، مانند «کتابخانه» و «شاهنامه»، حفظ شده‌اند. پسوند «ـگانه» پس از عدد نیز نیم‌فاصله می‌گیرد و صورت‌های «سی‌ام، سی‌امی، سی‌امین» با همین قاعده بررسی می‌شوند.

این قواعد فقط مواردی را بررسی می‌کنند که از شکل نوشتاری و اطلاعات واژه‌نامه بتوان تشخیص داد. تشخیص معنای جمله، نقش دستوری وابسته به بافت، یا همهٔ استثناهای گونه‌های خاص واژگان هنوز در این افزونه پوشش داده نمی‌شود.
