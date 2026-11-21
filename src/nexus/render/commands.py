"""Human command line. World actions still go through the ordinary action validator."""

import json
import shlex
import sys

META = ("look", "mission", "evidence", "log", "help", "quit")
FIELDS = {
    "take": ("artifact",), "drop": ("artifact",), "move": ("target",),
    "probe": ("machine", "artifact"), "operate": ("machine", "artifact"),
    "configure": ("machine", "settings"), "finish": (), "wait": (), "observe": (),
}


def parse(line, actions):
    if line.startswith("{"):
        return json.loads(line)
    verb, *args = shlex.split(line)
    verb = verb.lower()
    if verb not in actions or verb not in FIELDS:
        raise ValueError("Unknown command for this world. Type help for the available commands.")
    fields = FIELDS[verb]
    if verb == "configure" and len(args) >= 2:
        try:
            # Preserve JSON quotes: shlex would otherwise turn ["1"] into [1].
            lexer = shlex.shlex(line, posix=True)
            lexer.whitespace_split = True
            lexer.commenters = ""
            next(lexer)  # command
            next(lexer)  # machine
            raw = lexer.instream.read().strip()
            settings = json.loads(raw) if raw.startswith("[") else [int(s) for s in args[1:]]
            if not isinstance(settings, list) or not settings or any(type(v) is not int for v in settings):
                raise ValueError("settings must be a nonempty integer array")
            return {"type": verb, "machine": args[0], "settings": settings}
        except ValueError:
            raise ValueError("Usage: configure MACHINE INTEGER ... or configure MACHINE [INTEGER,...]. Use integers only.") from None
    if len(args) != len(fields) or verb == "configure":
        usage = "MACHINE INTEGER ..." if verb == "configure" else " ".join(f.upper() for f in fields)
        raise ValueError(f"Usage: {verb} {usage}".rstrip())
    return {"type": verb, **dict(zip(fields, args, strict=True))}


def candidates(before_cursor, actions, files, view, *, devices=()):
    words = before_cursor.split()
    if not words or before_cursor[-1:].isspace():
        words.append("")
    *context, prefix = words
    choices = ()
    if not context:
        choices = (*META, *actions)
    elif context == ["help"]:
        choices = devices
    elif context == ["evidence"]:
        choices = files
    elif context == ["move"]:
        choices = view.exits
    elif context == ["take"]:
        choices = [x.id for x in (*view.visible_artifacts, *view.visible_stocks)]
    elif context == ["drop"] or (len(context) == 2 and context[0] in ("operate", "probe")):
        choices = [x.id for x in view.carried_artifacts]
    elif len(context) == 1 and context[0] in ("probe", "operate", "configure") and context[0] in actions:
        choices = [x.id for x in view.visible_machines]
    return sorted({s for s in choices if s.startswith(prefix)})


def reader(console, actions, files, *, devices=()):
    # No persistent or cross-session history. Preserve pipes, redirected input and CLI tests.
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return lambda view: console.input("[bold cyan]nexus>[/bold cyan] ")
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.shortcuts import CompleteStyle

    class Visible(Completer):
        def get_completions(self, document, complete_event):
            line = document.text_before_cursor
            prefix = line.split()[-1] if line and not line[-1].isspace() else ""
            for word in candidates(line, actions, files, current, devices=devices):
                yield Completion(word, start_position=-len(prefix))

    prompt = PromptSession(completer=Visible(), complete_while_typing=False, complete_style=CompleteStyle.READLINE_LIKE)

    def read(view):
        nonlocal current
        current = view
        return prompt.prompt("nexus> ")

    current = None
    return read


def log_entry(action, response):
    kind = "Rejected" if not response.ok else "Probe" if action.type == "probe" else (
        "Observation" if action.type == "observe" else "Applied")
    params = action.model_dump(mode="json", exclude={"type"})
    args = " ".join(str(v) for v in params.values())
    detail = response.message
    if not detail:
        # Some worlds use structured readings instead of a status sentence.
        detail = json.dumps(list(response.events), ensure_ascii=False, separators=(",", ":"))
    return f"Turn {response.current_turn} | {kind}: {action.type} {args}".rstrip() + (f" | {detail}" if detail else "")
