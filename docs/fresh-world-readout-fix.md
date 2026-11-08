# Fresh-world control-admission fix — 3 November 2026

**Historical patch.** The package builder reads the original correction from Git commit
`7e2b74e5c16a8afd4687bfaf4538bbba72592ed6`; that commit must be available in your clone.
Use this patch only with the November 3 package. New panel packages already include
their own launcher, readout and run guide.

The initial run completed ten Astra tasks successfully: six historical anchors and
four fresh controls. The launcher then falsely rejected the controls because
MindTrial recorded text-response-format: false while the YAML omitted this default.

This is a NEXUS readout/configuration comparison bug. No completed task needs to
be repeated, and no inference setting needs to change.

## Apply and resume

Unpack NEXUS-fresh-control-fix-2026-11-03.zip into ~/Downloads. Keep the original
NEXUS-fresh-world-test-run-2026-11-03 directory with its results in place. With the
same MindTrial binary and provider credentials, run:

```bash
bash "$HOME/Downloads/NEXUS-fresh-control-fix-2026-11-03/resume.sh"
```

The script applies the host-only correction, resumes Astra's 22 fresh challenges,
then runs Luna, Flash and Grok on all 26 fresh conditions each. That is **100
remaining attempts**, with no automatic repetitions. It uses the existing pinned
image and --skip-build, so no fetch or Docker rebuild is needed for this recovery.
It stops on the first nonzero exit, including admission, coverage and 429 blockers.

For a different original package location:

```bash
bash "$HOME/Downloads/NEXUS-fresh-control-fix-2026-11-03/resume.sh" \
  /absolute/path/to/NEXUS-fresh-world-test-run-2026-11-03
```

To apply the correction without starting a model run:

```bash
python3 "$HOME/Downloads/NEXUS-fresh-control-fix-2026-11-03/apply.py"
```

Then individual suites can be selected through the original run.sh. Do not use
the original run-all.sh to resume this attempt: it starts the anchors again.
This recovery sequence assumes the ten supplied attempts are the completed work;
if more tasks have since run, select only the outstanding models/suites/rows.

## What changes

Only summarize_results.py in the original package is replaced. The corresponding
release checksum is updated, and operator_updates records this correction's
source commit and old/new hashes. The original release and readout are backed up
under operator-updates/fresh-readout-defaults-v1/. Reapplying the same fix is safe.

The world image/source commit remains 3ded3ba1a83815ed12950529619b344b23186e68.
Configs, task objects, model settings, original result folders and their manifests
are unchanged. The launcher can therefore reuse the four valid Astra controls
under the same exact configuration and MindTrial binary. It still rejects a
changed binary, actual inference drift, failed receipts or invalid provenance.

The correction recognizes two concrete false defaults in MindTrial:
text-response-format and Google's text-response-format-with-tools. True values
still count as changes, as do other boolean/numeric differences. It does not
ignore all false values or infer that unknown parameters are harmless.

## Initial findings

All ten tasks have recorded world victories and accepted receipts. Terminal
diagnostics report nine evidence-supported wins. S08 is the exception: it wins in
24 actions with three mechanisms still compatible with its evidence, so it is a
compatible win rather than a guaranteed inference. The hidden repair anchors
S22/S23/S24 report supported wins in 27/27/33 actions. F01/F03/F05/F08 use 4/4/5/6
actions and all report supported wins. The fresh hidden-law and planning tasks
have not yet run.

These observations come from the supplied JSON, logs and matching provenance.
They do not constitute a new canonical-replay audit or reconstruction of original
HMAC secrets. Preserve the complete results directory, including these ten
attempts, when collecting the remaining results.
