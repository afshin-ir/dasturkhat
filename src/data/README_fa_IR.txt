Source
======
https://github.com/b00f/lilak

License
=======
Lilak, Persian Spell Checking Dictionary

Copyright 2015 Mostafa Sedaghat Joo

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

README
======
Lilak is an open source project for generating Persian dictionary for hunspell spell checker based on Persian Morphology.
This dictionary is free and the source is available under Apache License Version 2.0.



بررسی رسم‌الخط مرجّح در لیبره‌آفیس (آزمایشی)
=================================================

بستهٔ OXT لیبره‌آفیس، افزون‌بر فرهنگ املایی هان‌اسپل، یک بررسی‌کنندهٔ آفلاین
برای صورت‌های نامرجّحِ برخی قواعد دستور خط دارد و صورت مرجّح را پیشنهاد می‌دهد.
این بررسی‌کننده از سازوکار بررسی دستور زبان لیبره‌آفیس استفاده می‌کند.

قواعد پوشش‌داده‌شده در این نسخه:

* نیم‌فاصلهٔ پیشوند فعلی «می/نمی/همی»: «می شود» ← «می‌شود»، «میشود» ← «می‌شود».
* نیم‌فاصلهٔ پسوند جمع «ها»: «کتابها» و «کتاب ها» ← «کتاب‌ها».
* نیم‌فاصله در ترکیب‌های «این/آن + طور/گونه»: «اینطور» یا «این طور» ← «این‌طور».

برای دیدن زیرخط هنگام تایپ، گزینه‌های «بررسی املا هنگام تایپ» و «بررسی دستور زبان هنگام تایپ»
باید در تنظیمات ابزارهای نوشتاری روشن باشند. زبان متن نیز باید فارسی باشد.

این قابلیت در Writer نسخهٔ ۲۶٫۸٫۲٫۲ نصب و به‌صورت عملی بررسی شده است. دامنهٔ قواعد
هنوز محدود است و قواعد جدید باید پیش از افزوده‌شدن با متن کتاب دستور خط تطبیق داده شوند.
