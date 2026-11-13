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

بررسی رسم‌الخط مرجّح در LibreOffice Writer
==========================================

بستهٔ OXT، افزون‌بر فرهنگ املایی هان‌اسپل، یک بررسی‌کنندهٔ آفلاین برای
برخی صورت‌های نامرجّحِ دستور خط دارد. این بررسی‌کننده از زیرسامانهٔ بررسی
دستور زبان Writer استفاده می‌کند و صورت مرجّح را برای جایگزینی پیشنهاد می‌دهد.
مرجع قواعد کتاب «دستور خط فارسی» فرهنگستان زبان و ادب فارسی، ویراست دوم است.

گروه‌های قواعد پیاده‌شده
-------------------------

* پیشوندهای فعلی «می/نمی/همی» با نیم‌فاصله؛ پیشوندهای فعلی «ب/ن/م» با
  اصلاح املای پیشوند و نمونه‌های تغییر الف؛ «همی» تأکیدی از قاعده مستثناست.
* پسوند جمع «ها»؛ نیم‌فاصله برای صورت‌های متصل و پیشنهاد نیم‌فاصله برای
  صورت‌های جدا، در مواردی که پایه در دادهٔ واژگانی شناخته شود.
* ترکیب‌های واژگانی‌شده با «هر» و «هیچ»، ترکیب‌های فهرست‌شدهٔ «همین/همان»،
  و «این/آن + طور/گونه».
* پسوندهای «تر/ترین»، «وار/سان/آسا/آگین/باره/جات/فام/وش»، «گر/گری»،
  «واره»، «خانه/نامه» و «گانه» با توجه به پایهٔ واژگانی و استثناهای ثبت‌شده.
* پیشوندهای فعلی و پیشوندواره‌های فهرست‌شده در کتاب، از جمله صورت‌های
  نیازمند نیم‌فاصله و مواردی که پیوسته نوشته می‌شوند.
* نمونه‌هایی از ترکیب‌های تکراری، ترکیب با اسم خاص، ترکیب‌های صفتی و
  عبارت‌های چندواژه‌ایِ حروف اضافه و ربط که در متن کتاب صریحاً آمده‌اند.
* صورت‌های نامرجّحِ درج‌شده در جدول‌های واژه‌های چنداملاییِ عام و نام‌های
  خاص؛ در کنار آن‌ها، ۱۱۰ الگوی عبارتِ چندواژه‌ای و مثال صریح نیز در فایل
  `preferred-spellings.json` نگهداری می‌شود. این فایل در مجموع ۲۱۲ جایگزینی
  مستقیم دارد.

دامنه و محدودیت
---------------

این افزونه بررسی دستور زبان یا معنا انجام نمی‌دهد. مواردی که شکل درستشان
به معنی جمله، نقش دستوری، تلفظ، یا زمینهٔ تاریخی و نام‌شناختی وابسته است،
تا جای ممکن خودکار اصلاح نمی‌شوند. فهرست عبارت‌ها و واژه‌های استثنایی نیز
فقط شامل موارد صریح و قابل‌تشخیص است؛ بنابراین این افزونه همهٔ قواعد و
همهٔ ترکیب‌های ممکن کتاب را پوشش نمی‌دهد.

برای دیدن زیرخط هنگام تایپ، گزینه‌های «Check spelling as you type» و
«Check grammar as you type» باید در تنظیمات Writer روشن باشند و زبان متن
فارسی تنظیم شده باشد.
