# Quickstart

Run from a directory you authorize Guara to use. Commands create a local `.opentruth/` store.
For a self-contained temporary demonstration, run `python -m examples.tutorial` from the source
checkout or extracted complete release ZIP. All examples below are synthetic.

## Record a source and a claim

```sh
opentruth init
opentruth source add "SYNTHETIC notebook" --type EXPERIMENT
opentruth claim add "SYNTHETIC: beam is 1 m long." --subject beam --predicate length --value 1 --unit m --actor "synthetic demonstrator"
opentruth claim list --query beam --subject beam
```

The source and claim additions return JSON records with generated `id` values. In the following
commands, replace `CLAIM_UUID` and `SOURCE_UUID` with those actual values; these labels are placeholders.
A new claim needs review. Registering source metadata does not evaluate its scientific quality.

## Connect evidence and review

```sh
opentruth evidence link CLAIM_UUID SOURCE_UUID --relationship SUPPORTS --location "table 1" --excerpt "SYNTHETIC measurement: 1 m" --actor "synthetic demonstrator"
opentruth --format text claim inspect CLAIM_UUID
opentruth review CLAIM_UUID --decision INCONCLUSIVE --reason "Synthetic demonstration only" --actor "synthetic reviewer"
opentruth history CLAIM_UUID
```

Inspection reports `SUPPORTED_BY_REGISTERED_EVIDENCE` after the explicit support link.
This records a relationship, not independent verification. Human review status remains separate.
Acceptance (`ACCEPTED_FOR_USE`) and rejection (`REJECTED`) require a nonblank reason.

## Correct and reassess

Copy the evidence link's returned `id` into `LINK_UUID`:

```sh
opentruth claim revise CLAIM_UUID --statement "SYNTHETIC: beam is 2 m long." --value 2 --reason "SYNTHETIC transcription correction" --actor "synthetic editor"
opentruth claim inspect CLAIM_UUID
opentruth evidence revise LINK_UUID --relationship CONTRADICTS --reason "SYNTHETIC reassessment against the corrected claim" --actor "synthetic assessor"
```

The correction preserves the original version, resets review status to `NEEDS_REVIEW`, and makes
previous links require reassessment. Inspection initially reports `INSUFFICIENT_EVIDENCE`; the
explicit contradictory reassessment then reports `CONTRADICTED_BY_REGISTERED_EVIDENCE`.
Use the actual assessor's attribution for reassessment rather than another person's identity.

## Export and back up

```sh
opentruth export > evidence.json
opentruth backup snapshot.zip
opentruth restore snapshot.zip --data-dir restored-evidence
```

Export is metadata-only; backup includes registered source bytes. Restore requires an absent
destination data directory. See [backup and integrity](backup-and-integrity.md).

## JSON automation remains available

Equivalent input shapes continue to work:

```sh
opentruth claim list --json '{"query":"beam","subject":"beam","limit":100}'
```

Do not supply the same field in JSON and as a convenience argument; the command rejects the
ambiguity without changing records. See [all flags](cli-reference.md), [comparison context and
tolerances](conflict-detection.md), and [installation](installation.md).
