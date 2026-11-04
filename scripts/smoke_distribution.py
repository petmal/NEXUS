"""Build wheel/sdist, install each in isolation, and exercise public CLI/replay."""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args, **kwargs):
    subprocess.run([str(a) for a in args], check=True, **kwargs)


def main():
    with tempfile.TemporaryDirectory(prefix='nexus-distribution-') as temp:
        scratch = Path(temp)
        output = scratch / 'dist'
        run('uv', 'build', '--out-dir', output, cwd=ROOT)
        distributions = sorted(p for p in output.iterdir() if p.name.endswith((".whl", ".tar.gz")))
        if len(distributions) != 2 or {p.suffix for p in distributions} != {'.whl', '.gz'}:
            raise RuntimeError('expected one wheel and one source distribution')
        for index, package in enumerate(distributions):
            work = scratch / f'install-{index}'
            work.mkdir()
            env = work / 'venv'
            run('uv', 'venv', '--python', '3.14.7', env)
            python = env / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
            nexus = env / ('Scripts/nexus.exe' if os.name == 'nt' else 'bin/nexus')
            # Resolve external dependencies from the exact project lock, then
            # install only our built artifact. Never use the editable checkout.
            requirements = work / 'requirements.txt'
            run('uv', 'export', '--frozen', '--no-dev', '--no-emit-project',
                '--format', 'requirements-txt', '--output-file', requirements, cwd=ROOT)
            run('uv', 'pip', 'install', '--python', python, '-r', requirements)
            run('uv', 'pip', 'install', '--python', python, '--no-deps', package)
            clean_env = {k: v for k, v in os.environ.items() if k not in ('PYTHONPATH', 'VIRTUAL_ENV')}
            options = dict(cwd=work, env=clean_env)
            run(nexus, '--help', **options)
            run(nexus, 'demo', **options)
            run(nexus, 'generate', 'world', '--seed', '17', '--planning-level', '0', **options)
            run(nexus, 'qualify', 'world/private.json', **options)
            run(nexus, 'solve', 'world/private.json', '--trace-out', 'trace.jsonl', **options)
            run(nexus, 'replay', 'world/private.json', 'trace.jsonl', **options)
            run(python, '-c', 'from nexus.ontology.repair.qualification import require_release; require_release()', **options)
            print(f'Clean installation passed: {package.name}')


if __name__ == '__main__':
    main()
