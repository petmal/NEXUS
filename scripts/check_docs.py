"""Check local file links in current entry-point documentation (no network)."""
from pathlib import Path
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    'README.md', 'CONTRIBUTING.md', 'SECURITY.md', 'docs/README.md',
    'docs/play-guide.md', 'docs/evaluation-guide.md', 'docs/research-guide.md',
    'docs/release-readiness.md', 'docs/reference/protocol.md',
    'docs/facility-setting.md', 'docs/future-experiments.md', 'docs/ontology-author-guide.md',
)


def main():
    errors = []
    for name in FILES:
        path = ROOT / name
        if not path.is_file():
            errors.append(f'{name}: missing document')
            continue
        source = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
        for link in re.findall(r'\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)', source):
            if ':' in link or link.startswith('#'):
                continue
            target = unquote(link.split('#', 1)[0])
            if target and not (path.parent / target).exists():
                errors.append(f'{name}: missing link target {target}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Local file links passed in {len(FILES)} current documents (anchors/external URLs not checked).')


if __name__ == '__main__':
    main()
