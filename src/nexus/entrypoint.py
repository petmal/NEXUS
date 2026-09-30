from __future__ import annotations

import sys


_FAST_COMMANDS = frozenset({"health", "request", "validate"})


def main() -> None:
    args = sys.argv[1:]
    if args and args[0] in _FAST_COMMANDS:
        from nexus.protocol.fast_cli import main as fast_main

        raise SystemExit(fast_main(args))

    from nexus.cli import app

    app()
