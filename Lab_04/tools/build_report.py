"""Build the Lab_04 book-domain report from source and real diagnostic logs."""
from pathlib import Path
import json
import shutil
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
QA = [('Що таке class?', 'Опис структури та поведінки об’єктів певного типу.'), ('Що таке object?', 'Конкретне значення в Python зі станом, типом та ідентичністю.'), ('Що таке instance?', 'Об’єкт, створений на основі певного класу.'), ('Для чого __init__()?', 'Ініціалізує стан уже створеного instance; власне створення об’єкта виконує __new__.'), ('Що таке instance attribute?', 'Атрибут, який належить конкретному об’єкту, наприклад book._pages.'), ('Що таке class attribute?', 'Атрибут, заданий на рівні класу; спільний для instances, доки його не перевизначено на instance.'), ('Що таке encapsulation?', 'Контроль стану та правил його зміни через визначений інтерфейс об’єкта.'), ('Для чого properties?', 'Для доступу до контрольованої логіки як до атрибута; setter може перевіряти інваріанти.'), ('Чим property відрізняється від public field?', 'Property викликає getter/setter і може перевіряти значення; public field без додаткового механізму є прямим доступом до стану.'), ('Що таке inheritance?', 'Створення підтипу на основі базового класу зі спільною поведінкою та можливістю спеціалізації.'), ('Що означає relation is-a?', 'Відношення «є різновидом»: EBook є Book і повинна дотримуватися його контракту.'), ('Що таке composition?', 'Побудова поведінки об’єкта через використання інших об’єктів-компонентів.'), ('Що означає relation has-a?', 'Відношення «має складову»: Book має PublicationInfo, каталог має repository.'), ('Коли composition краща за inheritance?', 'Коли компоненти потрібно змінювати незалежно або немає справжнього відношення підтипу; вона зменшує залежність від базового алгоритму.'), ('Для чого super()?', 'Для делегування виклику наступній реалізації в method resolution order; корисно для узгодженої ініціалізації та cooperative inheritance.'), ('Що таке polymorphism?', 'Можливість використовувати різні реалізації через один сумісний інтерфейс.'), ('Що таке duck typing?', 'Підхід, за якого важлива потрібна поведінка об’єкта, а не лише його конкретний клас.'), ('Що таке ABC?', 'Abstract Base Class — базовий клас з абстрактним контрактом і можливими спільними реалізаціями.'), ('Для чого abstractmethod?', 'Позначає метод, який concrete subclass має реалізувати, щоб його можна було інстанціювати.'), ('Чи можна створити instance abstract class?', 'Якщо залишаються нереалізовані abstract methods — ні, буде TypeError. Повністю реалізований subclass створити можна.'), ('Що таке Protocol?', 'Опис структурного інтерфейсу: сумісний об’єкт повинен мати потрібні методи й атрибути.'), ('Чим Protocol відрізняється від ABC?', 'ABC зазвичай вимагає явної участі в ієрархії; Protocol дозволяє сумісність без наслідування за структурою.'), ('Що таке structural typing?', 'Сумісність типів визначається набором і сигнатурами доступних членів.'), ('Що таке nominal typing?', 'Сумісність пов’язана із явно оголошеною належністю до класу чи ієрархії.'), ('Що таке dataclass?', 'Декоратор, що автоматично генерує типові методи класу на основі анотованих полів.'), ('Які methods генерує dataclass?', 'За типовими налаштуваннями __init__, __repr__, __eq__; інші можливості, як ordering чи hash, залежать від параметрів.'), ('Для чого default_factory?', 'Створює окреме значення за замовчуванням для кожного instance, наприклад новий list.'), ('Чому mutable default є проблемою?', 'Спільний mutable default може непомітно ділитися між об’єктами. Dataclass відхиляє багато таких defaults; потрібна фабрика.'), ('Для чого __post_init__()?', 'Для додаткової ініціалізації, нормалізації та перевірок після автоматичного __init__.'), ('Що означає frozen=True?', 'Звичайні присвоєння полям і видалення полів забороняються. Це поверхнева незмінність, а не абсолютний захист від обходу чи змін вкладених mutable objects.'), ('Що означає slots=True?', 'Dataclass створює slots для полів; це зазвичай зменшує накладні витрати й обмежує довільні instance attributes, з урахуванням особливостей наслідування.'), ('Що таке dunder method?', 'Спеціальний метод з подвійними підкресленнями, який інтегрує клас у протоколи Python.'), ('Для чого __repr__()?', 'Для інформативного developer/debug представлення об’єкта.'), ('Для чого __str__()?', 'Для зрозумілого користувачеві текстового представлення.'), ('Для чого __len__()?', 'Для визначення len(object), наприклад кількості книг у каталозі.'), ('Для чого __iter__()?', 'Для отримання iterator під час iter(object) або for.'), ('Для чого __contains__()?', 'Для перевірки належності через value in object.'), ('Для чого __call__()?', 'Щоб instance можна було викликати як функцію.'), ('Що таке SOLID?', 'П’ять принципів проєктування: SRP, OCP, LSP, ISP та DIP.'), ('Що означає SRP?', 'Single Responsibility Principle: клас має одну основну відповідальність і причину зміни.'), ('Що означає OCP?', 'Open/Closed Principle: можливість розширення через нову поведінку без постійного редагування стабільного клієнтського коду.'), ('Що означає LSP?', 'Liskov Substitution Principle: підтип має замінювати базовий тип без порушення його контракту.'), ('Що означає ISP?', 'Interface Segregation Principle: декілька малих потрібних інтерфейсів краще за один надмірний.'), ('Що означає DIP?', 'Dependency Inversion Principle: високорівнева логіка залежить від abstractions, а не конкретних деталей інфраструктури.'), ('Що таке dependency injection?', 'Передавання залежностей ззовні, наприклад exporter через constructor замість створення всередині сервісу.'), ('Чому DI покращує testability?', 'Можна передати fake або stub, ізолювати бізнес-логіку й перевіряти її без реальної зовнішньої інфраструктури.'), ('Що таке type hint?', 'Анотація очікуваного типу змінної, параметра або результату функції.'), ('Чи перевіряє Python type hints автоматично в runtime?', 'Ні. Потрібні окремі runtime checks; annotations самі по собі не забороняють неправильні значення.'), ('Що таке static type checker?', 'Інструмент аналізу типових контрактів і сумісності до виконання програми.'), ('Для чого mypy?', 'Для static type checking Python-коду та виявлення несумісних аргументів, присвоєнь, return types та інших порушень типів.'), ('Для чого Pyright?', 'Альтернативний статичний аналізатор типів для Python, доступний у CLI та інтеграціях редакторів.'), ('Що таке TypeVar?', 'Параметр типу для generic code, що зберігає зв’язок типів між входом, станом і результатом.'), ('Що таке Generic?', 'Базовий засіб оголошення параметризованого класу в сумісному синтаксисі typing.'), ('Що означає Generic[T]?', 'Клас параметризується типом T; Repository[Book] і Repository[Author] є спеціалізаціями одного generic class.'), ('Що таке bound TypeVar?', 'TypeVar із верхньою межею типу чи Protocol; T може бути сумісним підтипом цієї межі.'), ('Що таке constrained TypeVar?', 'TypeVar з визначеним набором допустимих типів, наприклад TypeVar("Number", int, float); це не те саме, що upper bound.'), ('Що таке TypedDict?', 'Опис типів відомих ключів словника; runtime-значення залишається звичайним dict.'), ('Чим TypedDict відрізняється від dataclass?', 'TypedDict описує mapping; dataclass створює class instances з методами й можливою валідацією.'), ('Коли доцільно використовувати TypedDict?', 'Для зовнішніх payloads, JSON-подібних структур і API-даних з відомими ключами.'), ('Чому external payload і domain object краще розділяти?', 'Зовнішня схема й domain invariants мають різні обов’язки; явна фабрика відокремлює інтеграцію від бізнес-моделі та полегшує перевірку й еволюцію.')]


def build() -> None:
    doc = Document()
    section = doc.sections[0]
    section.page_width,section.page_height = Cm(21),Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2)
    section.left_margin,section.right_margin = Cm(2.5),Cm(1.5)
    for name in ('Normal','Title','Heading 1','Heading 2'):
        style = doc.styles[name]
        style.font.name = 'Times New Roman'
        style.font.size = Pt(12 if name == 'Normal' else 14)
        style.font.color.rgb = RGBColor(0,0,0)
    for border in doc.styles.element.xpath('.//w:pBdr'):
        border.getparent().remove(border)
    doc.styles['Normal'].paragraph_format.line_spacing = 1.08
    doc.styles['Normal'].paragraph_format.space_after = Pt(6)

    def p(text):
        return doc.add_paragraph(text)

    def h(text):
        doc.add_heading(text,level=1)

    def page(text):
        doc.add_page_break()
        h(text)

    def code(text,size=8.5):
        para = p('')
        para.paragraph_format.line_spacing = 1
        run = para.add_run(text.strip())
        run.font.name,run.font.size = 'Consolas',Pt(size)

    def source(name):
        return (ROOT/'src/book_domain'/name).read_text(encoding='utf-8')

    def picture(name,caption,width=16.5):
        doc.add_picture(str(ROOT/'docs/screenshots'/(name+'.png')),width=Cm(width))
        p(caption)

    def table(headers,rows):
        t = doc.add_table(rows=1,cols=len(headers))
        t.style = 'Table Grid'
        if headers == ['Принцип','Застосування']:
            t.autofit = False
            t.columns[0].width,t.columns[1].width = Cm(2.4),Cm(14.1)
        for cell,value in zip(t.rows[0].cells,headers):
            cell.text = value
            cell.paragraphs[0].runs[0].bold = True
        for row in rows:
            for cell,value in zip(t.add_row().cells,row):
                cell.text = str(value)
        if headers == ['Принцип','Застосування']:
            for row in t.rows:
                row.cells[0].width,row.cells[1].width = Cm(2.4),Cm(14.1)

    cover = [
        ('ЛЬВІВСЬКИЙ НАЦІОНАЛЬНИЙ УНІВЕРСИТЕТ\nІМЕНІ ІВАНА ФРАНКА',14,65),
        ('ЗВІТ ДО ЛАБОРАТОРНОЇ РОБОТИ №4',16,20),
        ('«Професійне ООП та система типів Python»',14,18),
        ('з курсу «Професійний Python»\nВаріант №2 — «Система обліку книг»',14,45),
        ('Виконав: Бровді Олександр\nГрупа: ФеП-32\nПеревірив(ла): Свелеба Сергій Андрійович\nДата: 07.11.2026',12,70),
        ('Львів — 2026',14,0),
    ]
    for i,(text,size,after) in enumerate(cover):
        para = doc.add_paragraph(text,'Title' if i == 1 else None)
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.space_after = Pt(after)
        for run in para.runs:
            run.font.size = Pt(size)

    page('Мета та постановка задачі')
    p('Мета — побудувати типізовану об’єктну модель із класами, композицією, наслідуванням, ABC, Protocol, dataclass, properties, dunder methods, SOLID, Generic, TypeVar та TypedDict. Перевірити public API статичним аналізатором mypy й дослідити заміну залежностей.')
    p('Індивідуальний варіант 2 — система обліку книг. Реалізовано додавання книги, пошук за автором і назвою, фільтрацію за роком, визначення найбільшої книги, repository, search/reporting service та exporter Protocol. Дані зберігаються в пам’яті; JSON та CSV є форматами експорту.')
    h('Предметна область та сутності')
    p('Book описує книгу з ID, назвою, автором, відомостями про видання й кількістю сторінок. Author задає ідентифікованого автора. PublicationInfo — незмінний value object року й видавництва. BookCatalog керує колекцією книг через repository. LibraryRegistry об’єднує сценарії бібліотеки. EBook спеціалізує Book електронним форматом і зберігає його контракт.')
    h('Структура проєкту')
    code('''book-management-system-lab-04/
├── pyproject.toml, README.md, .gitignore
├── src/book_domain/
│   ├── models.py, value_objects.py, catalog.py
│   ├── protocols.py, repositories.py, dto.py, exporters.py
│   ├── services.py, design_experiments.py, exceptions.py
│   └── main.py, __init__.py, __main__.py, py.typed
├── tests/test_domain.py
├── experiments/type_errors_before.py.txt
├── experiments/type_errors_after.py.txt
├── tools/, docs/results/, docs/screenshots/
├── docs/Lab_04_Report_Variant_2.docx
└── Lab_04/ (автономна копія коду й експериментів)
    └── report/report.docx''')
    p('У репозиторії є звіт лише до Lab_04. Збережено src-layout і симетричну структуру кореневої та вкладеної копій, як у попередніх роботах.')

    page('Діаграма класів та зв’язки')
    picture('class_diagram','Рисунок 1. Схема domain classes і основних залежностей.')
    p('EBook is-a Book — виправдане наслідування для підтипу книги. Book has-a Author і PublicationInfo — композиція складових. BookCatalog has-a Repository[Book], LibraryRegistry has-a BookCatalog та сервіси. Для розширення поведінки перевагу надано композиції й залежностям від інтерфейсів.')
    code('''Repository[T] (ABC) <- InMemoryRepository[T]
BookCatalog -> Repository[Book]
ExportService -> Exporter (Protocol)
JsonExporter / CsvExporter / FakeExporter satisfy Exporter
LibraryRegistry -> SearchService + ReportingService + ExportService''',9)
    p('Схема спрощена: стрілки has-a/uses показують програмні залежності й посилання, а не жорстке володіння життєвим циклом усіх об’єктів. Один Author може використовуватись кількома книгами.')

    page('Dataclass та immutable value object')
    code(source('value_objects.py'))
    model = source('models.py')
    code(model[model.index('@dataclass'):model.index('class Book:')])
    p('PublicationInfo є frozen value object: однакові значення порівнюються за полями; рік і видавництво не змінюються через звичайний інтерфейс. Author також використовує frozen dataclass. slots=True обмежує набір атрибутів. __post_init__ перевіряє runtime-інваріанти й нормалізує текст.')
    p('Третій dataclass, CatalogReport, містить DTO результату аналітики. Для mutable defaults у dataclass потрібний field(default_factory=...); у реалізованих value objects змінюваних значень за замовчуванням немає.')

    page('Encapsulation та property книги')
    book = model[model.index('class Book:'):model.index('class EBook')]
    constructor = book[:book.index('    @property')]
    pages = book[book.index('    @property\n    def pages'):book.index('    def __str__')]
    code(constructor)
    code(pages)
    p('ID, назва, автор і відомості про видання доступні для читання через properties. Кількість сторінок змінюється через setter: додатне ціле значення перевіряється до зміни _pages. Неправильне оновлення залишає попередній стан. bool і дробові значення відхиляються.')
    p('ClassVar kind описує поведінку на рівні класу, а _id, _title, _author, _publication і _pages є instance attributes. Підкреслення — конвенція доступу, а не механізм безпеки. Валідація бізнес-даних виконується окремо від static type checking.')

    page('Наслідування та dunder methods')
    code(model[model.index('class EBook'):])
    code(book[book.index('    def __str__'):])
    p('super().__init__ делегує базову валідацію Book. EBook додає лише формат epub/pdf, не змінюючи очікувань пошуку чи звітності. Підстановка EBook до BookCatalog і вибір її як найбільшої книги перевірені тестом LSP.')
    h('Природний інтерфейс колекції')
    code('''len(catalog)       # __len__
for book in catalog:  # __iter__
    print(book)       # __str__
1 in catalog       # __contains__: пошук ID
catalog[0]         # __getitem__: позиція у порядку додавання
repr(catalog[0])    # __repr__: developer representation''',9)
    p('У каталозі реалізовано __len__, __iter__, __contains__, __getitem__ та __str__, а в Book — __repr__ і __str__. Індекс позиції та ID є різними поняттями: catalog[0] — перша книга, catalog.get(1) — книга з ID 1.')

    page('Generic repository та bound TypeVar')
    code(source('repositories.py'))
    p('T = TypeVar("T", bound=HasId) обмежує параметр типу об’єктами з ID. Repository[T] — abstract base class; створити його instance без реалізації abstract methods не можна. InMemoryRepository[Book] та InMemoryRepository[Author] використовують один клас, але зберігають зв’язок типу add/get/all.')
    p('Повторний ID спричиняє DuplicateIdError і не перезаписує попередню книгу. all() повертає tuple-сnapshot, тому клієнт не отримує внутрішній dict. BookCatalog залежить від Repository[Book], а не від конкретного InMemoryRepository.')

    page('TypedDict та фабрика domain objects')
    code(source('dto.py'),8)
    p('BookPayload — структура зовнішніх даних; file_format є NotRequired. book_from_payload створює Author, PublicationInfo та потрібний Book/EBook. book_to_payload виконує зворотне перетворення. TypedDict у runtime залишається dict і не виконує автоматичної валідації довільного JSON; валідацію значень тут забезпечують конструктори.')
    p('Для встановленого типізованого пакета додано py.typed та package-data. Це дозволяє mypy аналізувати типи пакетних імпортів у незалежному експериментальному файлі.')

    page('Protocol та interchangeable exporters')
    code(source('protocols.py'))
    code(source('exporters.py'),8)
    p('JsonExporter і CsvExporter не успадковують Exporter явно. Сумісність визначається методом export(records) -> str. runtime_checkable дозволяє isinstance(adapter, Exporter), але не перевіряє повну сигнатуру чи бізнес-поведінку; це не заміна mypy і тестів.')

    page('Search та reporting services')
    service = source('services.py')
    code(service[service.index('class SearchService'):service.index('class ExportService')],8)
    p('Автор шукається точно після нормалізації регістру й пробілів. Назва — за входженням підрядка без урахування регістру. Порожній пошуковий рядок повертає порожній результат. Фільтр року точний. Порожній каталог дає середнє 0.0 і largest=None; за рівних обсягів обирається перша книга.')

    page('Application service та dependency injection')
    code(service[service.index('class ExportService'):],8)
    p('LibraryRegistry оркеструє реєстрацію, пошук, звітність і експорт; відповідальні за окремі операції класи залишаються самостійними. Concrete repository та exporter обирає composition root create_demo_registry у main.py.')
    code('''catalog = BookCatalog(InMemoryRepository[Book]())
registry = LibraryRegistry("Навчальна бібліотека", catalog, JsonExporter())
csv_service = ExportService(catalog, CsvExporter())
test_service = ExportService(catalog, FakeExporter())''',9)
    p('Заміна формату чи test double не потребує зміни ExportService. FakeExporter не звертається до мережі чи файлів, повертає детермінований рядок і рахує виклики.')

    page('Застосування SOLID')
    table(['Принцип','Застосування'],[
        ('SRP','Book контролює стан; Repository зберігає; SearchService шукає; exporter форматує.'),
        ('OCP','Нова реалізація Exporter додається без зміни ExportService.'),
        ('LSP','EBook використовується в усіх операціях каталогу як Book.'),
        ('ISP','HasId та Exporter — вузькі інтерфейси; experiment має окремі Parser, Validator і Formatter.'),
        ('DIP','Високорівневий код залежить від Repository та Exporter, а concrete objects передаються ззовні.'),
    ])
    h('Обов’язковий design experiment')
    design = source('design_experiments.py')
    code(design[design.index('class HardwiredExportService'):design.index('class FakeExporter')],8)
    p('Варіант A створює JsonExporter сам: для заміни потрібна зміна реалізації або patch. Варіант B отримує Exporter через constructor; fake передається напряму, тому тест простіший і незалежний від формату. Саме B відповідає DIP. Композиція з abstraction знижує coupling, бо клієнт знає контракт, а не деталі адаптера.')
    evidence = json.loads((ROOT/'docs/results/design.json').read_text(encoding='utf-8'))
    code('DI result: '+evidence['injected']+'\nFake calls: '+evidence['fake_calls'],9)

    page('Inheritance vs composition experiment')
    design = source('design_experiments.py')
    code(design[design.index('class BaseTitleProcessor'):design.index('class TitleParser')],8)
    code(design[design.index('class ComposedTitleProcessor'):design.index('def run_design_experiments')],8)
    p('Обидва варіанти перетворюють "Кобзар; Мойсей" на "'+evidence['composition']+'" та відхиляють порожні назви. Наслідування зберігає спільний алгоритм у base class і дозволяє замінити parsing. Композиція дозволяє незалежно замінити Parser, Validator та Formatter, повторно використати компоненти й тестувати їх окремо.')
    p('Це поведінковий дослід, а не порівняння швидкості. Для стабільного алгоритму з однією точкою розширення inheritance простіше; для незалежних змін кількох кроків composition гнучкіша й не потребує комбінацій підкласів.')

    page('Обов’язковий type checking experiment')
    code((ROOT/'experiments/type_errors_before.py.txt').read_text(encoding='utf-8'))
    picture('type_errors_before','Рисунок 2. Реальні diagnostics mypy для трьох навмисних помилок.')
    table(['Помилка','Виправлення'],[
        ('assignment: str замість int','book_id: int = 1'),
        ('return-value: str замість int','total() повертає 100'),
        ('arg-type: Author замість Book','repository.add(Book(...))'),
    ])
    p('Некоректний приклад зберігається як .py.txt, щоб не потрапляти до production source. Runner створює тимчасовий .py, запускає справжній mypy і перевіряє рівно три diagnostics; після цього аналізує виправлений файл та весь src.')

    page('Виправлення та результат mypy')
    code((ROOT/'experiments/type_errors_after.py.txt').read_text(encoding='utf-8'))
    picture('type_errors_after','Рисунок 3. Виправлений експеримент проходить static checking.')
    picture('mypy','Рисунок 4. Production source проходить строгий mypy.')
    code('''[tool.mypy]
python_version = "3.11"
strict = true
warn_unused_ignores = true
warn_return_any = true
files = ["src"]''',9)
    p('Використано mypy. Типізація не змінює runtime semantics Python. Окремі runtime-перевірки залишаються потрібними для сторінок, року, ID та порожнього тексту. Public API всіх модулів src має annotations; tests містять навмисно неправильні runtime-входи й перевіряються запуском.')

    page('Результат роботи та перевірка')
    picture('application','Рисунок 5. Фактичний запуск демонстраційного сценарію.')
    p('Додано 4 книги; знайдено дві книги Івана Франка, одну назву «Кобзар» та книгу за 1911 роком. Найбільша — «Кобзар», 240 сторінок; середнє — 168.0. Дані сторінок є навчальними значеннями для умовних видань. Перевірено JSON і CSV export, dunder operations та structural Protocol.')
    p('Усі 14 автоматизованих тестів пройдено. Вони перевіряють інваріанти, property, frozen value object, EBook substitution, duplicate ID, порожній каталог, custom collection, generic repository для Author, ABC, fake exporter та еквівалентність двох design variants. Протоколи тестів і mypy збережено в docs/results.')
    p('Додатково реалізовано generic repository, bound TypeVar, runtime_checkable Protocol, custom collection, __getitem__/__iter__/__contains__, strategy pattern, repository abstraction, immutable value objects, exception hierarchy, окремі малі Protocols, фабрику та strict type-check command. Це перевищує мінімум трьох додаткових можливостей.')

    for start in range(0,60,10):
        page(f'Відповіді на контрольні запитання {start+1}–{start+10}')
        for i,(question,answer) in enumerate(QA[start:start+10],start+1):
            para = p('')
            para.paragraph_format.keep_with_next = True
            para.add_run(f'{i}. {question}').bold = True
            p(answer)

    page('Висновок')
    p('Створено типізовану об’єктну модель системи обліку книг за варіантом 2. Реалізовано необхідні domain classes, composition та обґрунтоване inheritance, dataclass і frozen value object, properties, ABC, Protocol, dunder methods, Generic, bound TypeVar та TypedDict. Бізнес-операції відокремлено від сховища й формату експорту.')
    p('Застосовано SOLID та dependency injection. Досліджено жорстку залежність і DI, а також inheritance і composition для однакової поведінки. Навмисні три помилки типів виявлено mypy, виправлено й повторно перевірено. Static checking доповнює runtime validation і тести, але не замінює їх.')
    h('Використані матеріали')
    p('Методичка Lab_04_узгоджено_з_Lab_01.docx: розділи 1–85; варіант 2 з розділу 47; type-checking experiment з розділу 71; design experiments з розділів 72–73; вимоги до звіту з розділу 83.')
    p('Репозиторій: https://github.com/Olexandr-Brovdi/book-management-system-lab-04')
    doc.core_properties.author = 'Бровді Олександр'
    doc.core_properties.title = 'Лабораторна робота 4 Система обліку книг Варіант 2'
    output = ROOT/'docs/Lab_04_Report_Variant_2.docx'
    doc.save(output)
    target = ROOT/'Lab_04/report/report.docx'
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(output,target)
    print(output)


if __name__ == '__main__':
    build()
