"""Check repository Markdown file links and heading links on the maintained reader paths."""

from functools import cache
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ENTRY = {
    'README.md', 'AGENTS.md', 'CONTRIBUTING.md', 'SECURITY.md', 'docs/README.md',
    'docs/play-guide.md', 'docs/evaluation-guide.md', 'docs/research-guide.md',
    'docs/release-readiness.md', 'docs/reference/protocol.md', 'docs/reference/metrics.md',
    'docs/facility-setting.md', 'docs/future-experiments.md', 'docs/ontology-author-guide.md',
    'docs/first-model.md', 'docs/benchmark-guide.md', 'docs/fresh-world-guide.md',
    'examples/mindtrial/fresh-world-run.md',
}


@cache
def prose(path):
    return re.sub(r'^`{3,}[^\n]*\n.*?^`{3,}\s*$', '', path.read_text(encoding='utf-8'),
                  flags=re.S | re.M)


@cache
def anchors(path):
    result = set()
    for title in re.findall(r'^#{1,6}\s+(.+?)\s*$', prose(path), flags=re.M):
        # GitHub heading conventions used in this repository, including duplicate suffixes.
        slug = ''.join(c for c in title.lower() if c in ' _-' or
                       unicodedata.category(c)[0] in 'LN').replace(' ', '-')
        candidate, suffix = slug, 0
        while candidate in result:
            suffix += 1
            candidate = f'{slug}-{suffix}'
        result.add(candidate)
    return result


def main():
    files = set(ROOT.glob('*.md'))
    for directory in ('docs', 'examples', '.github'):
        files.update((ROOT / directory).rglob('*.md'))
    errors = []
    for name in sorted(ENTRY):
        if ROOT / name not in files:
            errors.append(f'{name}: missing entry document')
    for path in sorted(files):
        name = path.relative_to(ROOT).as_posix()
        for link in re.findall(r'\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)', prose(path)):
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            dest = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not dest.exists():
                errors.append(f'{name}: missing link target {link}')
            elif name in ENTRY and dest.suffix == '.md' and url.fragment:
                if unquote(url.fragment) not in anchors(dest):
                    errors.append(f'{name}: missing heading {link}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Local file links passed in {len(files)} Markdown documents; '
          f'heading links checked from {len(ENTRY)} entry documents. External URLs not checked.')


if __name__ == '__main__':
    main()
