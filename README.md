# Система обліку книг

Лабораторна робота №4 «Професійне ООП та система типів Python».
**Бровді Олександр, ФеП-32. Варіант 2.** Професійний Python.

## Встановлення Python 3.11+

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m book_domain
book-domain --format csv --export docs/results/catalog.csv
python -m unittest discover -s tests -v
python -m mypy src
python tools/type_check_experiment.py
```

Linux/macOS: `source .venv/bin/activate`. Команди виконуються з кореня
або автономної папки Lab_04. Runtime не потребує сторонніх бібліотек.

## Реалізований варіант

Book, Author, BookCatalog, PublicationInfo та LibraryRegistry. EBook є Book
і підставляється у спільний каталог. Додавання, пошук за автором і назвою,
фільтрація за роком, найбільша книга, середнє та звіт. Пошук автора — точний,
без регістру й зайвих пробілів; назви — входження підрядка без регістру;
порожня назва пошуку не повертає всіх книг. Рік порівнюється точно.
Порожній каталог: average=0.0, largest=None. За рівних обсягів — перша книга.

Демонстрація: 4 книги, 2 книги Івана Франка, найбільша — «Кобзар», 240 стор.;
середнє — 168.0. Число сторінок задано для умовних навчальних видань.
ID додатний, сторінки додатні цілі, рік від 1 до поточного.
Повторний ID відхиляється, попередня книга не перезаписується.
Property pages не допускає некоректного оновлення; ID і складові книги
доступні для читання через properties. Підкреслення — конвенція інкапсуляції,
а не захист від навмисної зміни внутрішніх полів.

## Архітектура

```text
src/book_domain/
  models.py           — Author, Book, EBook
  value_objects.py    — frozen PublicationInfo
  catalog.py          — BookCatalog, custom collection
  protocols.py        — HasId та runtime_checkable Exporter
  repositories.py     — ABC Repository[T], InMemoryRepository[T]
  dto.py              — BookPayload TypedDict та фабрика
  exporters.py        — JSON і CSV стратегії
  services.py         — search/report/export, LibraryRegistry
  design_experiments.py — DI та inheritance/composition порівняння
  main.py             — composition root і демонстрація
tests/
experiments/          — before/after type errors у .py.txt
tools/                — перевірка, експерименти та звіт
docs/results/, docs/screenshots/
docs/Lab_04_Report_Variant_2.docx
Lab_04/src/, tests/, experiments/, tools/, pyproject.toml, README.md
Lab_04/report/report.docx
```

## SOLID та типізація

SRP: моделі контролюють стан, repository — зберігання, exporter — формат.
OCP: новий exporter додається без зміни ExportService.
LSP: EBook дотримується контракту Book.
ISP: HasId та Exporter описують лише потрібні методи.
DIP: каталог залежить від Repository[Book], експорт — від Exporter.
DI виконується вручну в create_demo_registry; fake exporter передається ззовні.

TypeVar T обмежено HasId. Той самий generic repository використано для Book
та Author. TypedDict задає зовнішню структуру, domain factory виконує валідацію
через конструктори. Анотації самі не перевіряють довільний JSON під час запуску.
Команда mypy використовує strict=true для всього src.
Runtime-checkable Protocol перевіряє наявність потрібного члена, а не його
повну сигнатуру чи поведінку; сумісність типів перевіряє mypy.

## Обов’язкові експерименти

У type_errors_before.py.txt навмисно містяться три помилки: str замість int,
неправильний return type та Author замість Book у Repository[Book].
Runner створює тимчасовий .py, запускає mypy, зберігає фактичні diagnostics,
потім перевіряє виправлений приклад і весь src. Некоректний файл не входить
до production source. Результати — docs/results/type_errors_before.txt,
type_errors_after.txt, mypy.txt.

Порівняно hardwired service і DI з fake exporter, а також однакове перетворення
назв через inheritance та composition (Parser + Validator + Formatter).
Досліди є поведінковими, не вимірюванням швидкості. Результати однакові;
у composition компоненти змінюються незалежно, inheritance зручне для
стабільного спільного алгоритму з визначеною точкою розширення.

Додатково: generic repository, bound TypeVar, runtime_checkable Protocol,
custom collection, __getitem__/__iter__/__contains__, strategy pattern,
repository abstraction, immutable value object, exception hierarchy,
кілька малих Protocols, фабрика та strict type-checking command.

## Звіт

```text
python -m pip install -e ".[report]"
python tools/create_report_assets.py
python tools/build_report.py
python tools/validate_submission.py
```

Звіт містить diagram, код, SOLID, всі 60 відповідей, реальний вивід програми
та результати mypy до і після виправлень. Звіти інших лабораторних відсутні.
