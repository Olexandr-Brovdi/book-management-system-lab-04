"""Check Lab_04 identity, OOP source structure and actual checker evidence."""
from pathlib import Path
import ast
import re
from xml.etree import ElementTree
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def validate() -> None:
    reports = [ROOT/'docs/Lab_04_Report_Variant_2.docx', ROOT/'Lab_04/report/report.docx']
    if ROOT.name == 'Lab_04':
        reports = [ROOT/'report/report.docx']
    for report in reports:
        with ZipFile(report) as archive:
            tree = ElementTree.fromstring(archive.read('word/document.xml'))
        text = ' '.join(''.join(t.itertext()) for t in tree.iter(W+'t')).casefold()
        for phrase in ('лабораторної роботи №4', 'варіант №2', 'бровді олександр',
                       'система обліку книг', 'bookcatalog', 'libraryregistry',
                       'publicationinfo', 'protocol', 'generic', 'typeddict',
                       'mypy', 'dependency injection', 'solid', '60.'):
            if phrase not in text:
                raise ValueError(f'Missing report requirement: {phrase}')
        if set(re.findall(r'варіант\s*№?\s*(\d+)', text)) != {'2'}:
            raise ValueError('Conflicting variant numbers')
        if 'заставний денис' in text or 'система оцінювання студентів' in text:
            raise ValueError('Unrelated template content')
    assert {p.resolve() for p in ROOT.rglob('*.docx') if '.venv' not in p.parts} == {
        p.resolve() for p in reports}
    classes = {node.name for p in (ROOT/'src').rglob('*.py')
               for node in ast.walk(ast.parse(p.read_text(encoding='utf-8')))
               if isinstance(node,ast.ClassDef)}
    assert {'Book','Author','BookCatalog','PublicationInfo','LibraryRegistry',
            'Repository','Exporter'} <= classes
    if len(reports) == 2:
        assert reports[0].read_bytes() == reports[1].read_bytes()
        for folder in ('src','tests','experiments','tools'):
            for p in (ROOT/folder).rglob('*'):
                if (p.is_file() and '__pycache__' not in p.parts
                        and not any(part.endswith('.egg-info') for part in p.parts)):
                    assert p.read_bytes() == (ROOT/'Lab_04'/p.relative_to(ROOT)).read_bytes(),p
        results = ROOT/'docs/results'
        assert (results/'type_errors_before.txt').read_text(encoding='utf-8').count(': error:') == 3
        for name in ('type_errors_after','mypy'):
            assert 'Success: no issues found' in (results/(name+'.txt')).read_text(encoding='utf-8')
    print('PASS: Lab_04, variant 2, book domain, OOP structure and real type-check evidence.')


if __name__ == '__main__':
    validate()
