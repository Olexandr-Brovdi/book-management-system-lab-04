"""Capture real execution, tests, type diagnostics and a class diagram."""
from pathlib import Path
import json
import os
import subprocess
import sys
import textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def capture(args: list[str]) -> str:
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                            encoding='utf-8', env=dict(os.environ, PYTHONIOENCODING='utf-8'))
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout + result.stderr


def image(name: str, command: str, output: str) -> None:
    folder = ROOT/'docs/screenshots'
    folder.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 21)
    lines = []
    for line in (command+'\n\n'+output).expandtabs(4).splitlines():
        lines.extend(textwrap.wrap(line, width=88, subsequent_indent='  ') or [''])
    canvas = Image.new('RGB', (1200,len(lines)*29+48), '#16202b')
    draw = ImageDraw.Draw(canvas)
    for i,line in enumerate(lines):
        draw.text((24,24+i*29),line,font=font,fill='#edf2f7')
    canvas.save(folder/(name+'.png'))


def diagram() -> None:
    canvas = Image.new('RGB',(1400,1000),'white')
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',26)
    body = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
    def box(rect, name, detail):
        draw.rounded_rectangle(rect,radius=12,fill='#f1f5f9',outline='#334155',width=3)
        x,y,right,_ = rect
        draw.text(((x+right)/2,y+14),name,font=title,fill='black',anchor='mt')
        draw.text(((x+right)/2,y+54),detail,font=body,fill='black',anchor='mt')
    def arrow(points,label,where):
        draw.line(points,fill='#334155',width=3)
        x,y=points[-1]
        draw.polygon([(x,y),(x-8,y-15),(x+8,y-15)],fill='#334155')
        draw.text(where,label,font=body,fill='#334155')
    box((480,25,920,135),'LibraryRegistry','register / search / report / export')
    box((480,270,920,380),'BookCatalog','len / iter / contains / getitem')
    box((20,270,420,380),'SearchService','author / title / year')
    box((980,270,1380,380),'ReportingService','largest / average / count')
    box((480,510,920,620),'Book','id / title / pages property')
    box((20,790,430,900),'Author','frozen dataclass: id / name')
    box((490,790,950,900),'PublicationInfo','frozen: year / publisher')
    box((1000,790,1380,900),'EBook','Book subtype: file_format')
    arrow([(700,135),(700,270)],'has-a',(720,190))
    arrow([(480,80),(220,80),(220,270)],'uses',(235,170))
    arrow([(920,80),(1180,80),(1180,270)],'uses',(1195,170))
    arrow([(700,380),(700,510)],'contains 0..*',(720,440))
    arrow([(560,620),(225,700),(225,790)],'has author',(125,715))
    arrow([(720,620),(720,790)],'has value',(735,700))
    draw.line([(1180,790),(1180,565),(920,565)],fill='#334155',width=3)
    draw.polygon([(920,565),(940,553),(940,577)],fill='white',outline='#334155',width=3)
    draw.text((1190,680),'inherits',font=body,fill='#334155')
    draw.text((35,945),'BookCatalog -> Repository[Book]; ExportService -> Exporter (Protocol)',font=body,fill='black')
    canvas.save(ROOT/'docs/screenshots/class_diagram.png')


def main() -> None:
    python = str(ROOT/'.venv/Scripts/python.exe')
    if not Path(python).exists():
        python = sys.executable
    folder = ROOT/'docs/results'
    folder.mkdir(parents=True,exist_ok=True)
    capture([python,'tools/type_check_experiment.py'])
    demo = capture([python,'-m','book_domain','--format','csv','--export','docs/results/catalog.csv'])
    tests = capture([python,'-m','unittest','discover','-s','tests','-v'])
    (folder/'application.txt').write_text(demo,encoding='utf-8')
    (folder/'tests.txt').write_text(tests,encoding='utf-8')
    capture([python,'-m','book_domain','--export','docs/results/catalog.json'])
    image('application','python -m book_domain',demo)
    image('tests','python -m unittest discover -s tests -v',tests)
    for name in ('type_errors_before','type_errors_after','mypy'):
        image(name,'mypy --strict', (folder/(name+'.txt')).read_text(encoding='utf-8'))
    diagram()
    # Keep full design evidence separate from the display-oriented CLI output.
    result = capture([python,'-c',
                      'import json; from book_domain.main import create_demo_registry; '
                      'from book_domain.design_experiments import run_design_experiments; '
                      'print(json.dumps(run_design_experiments(create_demo_registry().catalog),ensure_ascii=False))'])
    (folder/'design.json').write_text(json.dumps(json.loads(result),ensure_ascii=False,indent=2),encoding='utf-8')


if __name__ == '__main__':
    main()
