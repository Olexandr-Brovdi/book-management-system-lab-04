"""Run real before/after type-checking experiments; require exactly three errors."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run_mypy(target: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, '-m', 'mypy', '--no-incremental',
                           '--config-file', str(ROOT/'pyproject.toml'), str(target)],
                          cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                          env=dict(os.environ, PYTHONIOENCODING='utf-8'))


def main() -> None:
    results = ROOT/'docs/results'
    results.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)/'type_errors_demo.py'
        for label, expected in [('before', 1), ('after', 0)]:
            path.write_text((ROOT/f'experiments/type_errors_{label}.py.txt').read_text(
                encoding='utf-8'), encoding='utf-8')
            result = run_mypy(path)
            output = (result.stdout + result.stderr).replace(str(path), path.name)
            (results/f'type_errors_{label}.txt').write_text(output, encoding='utf-8')
            print(output)
            if result.returncode != expected:
                raise RuntimeError(f'Unexpected mypy exit status for {label}')
            if label == 'before' and output.count(': error:') != 3:
                raise RuntimeError('The fixture must demonstrate exactly three errors')
    result = run_mypy(ROOT/'src')
    output = result.stdout + result.stderr
    (results/'mypy.txt').write_text(output, encoding='utf-8')
    print(output)
    if result.returncode:
        raise RuntimeError('Production code does not pass strict type checking')


if __name__ == '__main__':
    main()
