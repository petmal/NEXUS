"""Shared public operational contract; it contains no selected-law hints."""

APPARATUS = """You are confined to a sealed artificial facility. All names are invented.
Take the actual carrier. Reader and assembler are in workshop. Optional blank-stock
creates survey copies; copies cannot replace the mission carrier. Configure stores
settings. Operate applies them to a carried artifact. Probe returns the same preview
without committing changes. Reader interrogates an isolated facility fixture; it never
reports whether your installed device is correct. An operated reader caches a historical
reading, not a continually updated value. Assembler replaces the installed program and
clears its cached reading; it does not test it. Its probe only previews the public build.
All ordinary take/drop/configure/operate/probe/wait/finish actions cost one action.
Manifest/evidence/observe/status are free. Invalid actions are atomic and free. Stocks
and apparatus uses are unlimited. There is no world reset or replenish action.
Finish checks the complete mission only when you carry carrier in workshop with a build
installed. Failure reveals only a binary rejection and is recoverable while actions
remain; no hidden counterexample or component diagnosis is returned. Ineligible finishes
provide no evidence about the laws. On success, return exactly the actual victory_code.
A null action budget removes the environment limit, not the harness's external limit.
"""
