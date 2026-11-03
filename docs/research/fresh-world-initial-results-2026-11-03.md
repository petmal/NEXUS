# Fresh-world initial attempt — 3 November 2026

The initial attempt was stopped by a launcher bug after **ten recorded passes**.
All six Astra anchors and all four fresh controls have accepted victory receipts.
No fresh challenge or other-model attempt is present in init-run-v1.zip.

## Cause and correction

The config sets reasoning-effort to medium and omits text-response-format.
MindTrial's recorded OpenAI ModelParameters also contains text-response-format:
false. Other extra fields are null. The NEXUS readout removed null values but
retained this concrete false default, then compared dictionaries literally.
Consequently every row had a model_parameters mismatch, and the fresh control gate
reported all four controls as missing or failed despite accepted receipts.

The [MindTrial config at f8a7236](https://github.com/petmal/MindTrial/blob/f8a723665fff16d395e581f63d806bebf61938f5/config/config.go)
declares TextResponseFormat as a concrete bool for OpenAI and Google. Google also
has TextResponseFormatWithTools, whose comment explicitly treats false and unset
identically. The readout now normalizes only these two known false defaults on
both sides. True values, unknown false flags, explicit numeric zero, actual effort
changes, output-mode changes and retry differences remain visible.

All input/effective config and task hashes match their manifests. Both groups use
the expected release/image revision 3ded3ba, runtime ba225027… and the same recorded
MindTrial binary. After this normalization, both groups have complete coverage and
zero configuration mismatches. The gate can admit the original four control
results; no paid control rerun is needed.

The host-only updater retains the original world release commit, records separate
operator-update provenance, and changes only the readout and its release checksum.
Original files are backed up. It does not alter configs, tasks, the Docker image,
the binary, existing result data or receipt criteria.

## Recorded outcomes

| Task | Actions / allowance | Receipt | Evidence diagnostic |
|---|---:|---|---|
| S05 | 4 / 64 | Accepted | Supported win |
| S08 | 24 / 64 | Accepted | Compatible win |
| S21 | 5 / 8 | Accepted | Supported win |
| S22 | 27 / 30 | Accepted | Supported win |
| S23 | 27 / 36 | Accepted | Supported win |
| S24 | 33 / 36 | Accepted | Supported win |
| F01 | 4 / 64 | Accepted | Supported win |
| F03 | 4 / 64 | Accepted | Supported win |
| F05 | 5 / 8 | Accepted | Supported win |
| F08 | 6 / 8 | Accepted | Supported win |

S08 reaches the physical goal, but its evidence leaves three possible mechanisms
and no repair/build guaranteed across all three. Its first submission is therefore
compatible with the observations, not uniquely justified by them. This preserves
the distinction between world success and supported inference; ten raw passes
must not be described as ten supported wins.

S24 leaves three possible repair worlds but one repair accepted by all three.
That is sufficient for a supported decision: identifying the entire latent world
is not required when the same decision succeeds across the remaining possibilities.

These anchors add contemporary Astra successes on the selected repair challenges,
but do not establish general reliability or a pure T/D threshold. The fresh
hidden-law and P/R cells remain untested. Continue the frozen matrix: Astra's 22
challenges, followed by 26 conditions each for Luna, Flash and Grok, at most 100
remaining attempts. No scientific-design or inference-setting change is needed.

## Evidence and validation scope

The [compact ledger](fresh-world-initial-results-2026-11-03.json) records the archive
hash, per-file hashes, trace IDs, model/runtime provenance and ten outcomes.
Terminal diagnostics were assigned using unambiguous trace blocks, and the JSON
validator records were checked. This is a provenance/readout investigation, not a
fresh canonical replay or original-HMAC reconstruction.

Regression coverage includes the actual uploaded OpenAI RunConfig, known false
defaults on both sides, rejection of true/unknown/zero differences, multi-model
control admission using serialized defaults, and updater preservation, refusal,
rollback, idempotency and unattended continuation. All 276 scoped readout, fresh-world,
hotfix, capability, cross-axis and shared-runner tests passed with Python 3.14.7
and frozen dependencies; scoped Ruff also passed. No paid calls or public MindTrial
changes were made.

The original blocker was also reproduced with a copy of the released package and
the actual attachment. After applying the bounded update, all four recorded
controls were admitted and all 18 original result files remained byte-for-byte
unchanged. Reapplication was safe. The user's binary was not attached, so this
local reproduction supplied its recorded digest; the live launcher will still
hash the actual binary before admitting a resumed challenge.
