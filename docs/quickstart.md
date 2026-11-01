# Quickstart

Run from a directory you authorize Guara to read:

```sh
opentruth init
opentruth source add --json '{"title":"SYNTHETIC notebook","source_type":"EXPERIMENT"}'
opentruth claim add --json '{"original_statement":"SYNTHETIC: beam is 1 m long.","subject":"beam","predicate":"length","value":1,"unit":"m","context":{"method":"synthetic ruler"}}'
opentruth claim list --json '{"subject":"beam"}'
```

The first two additions return JSON records containing generated UUIDs. Substitute these IDs:

```sh
opentruth evidence link --json '{"claim_id":"CLAIM_UUID","source_id":"SOURCE_UUID","relationship":"SUPPORTS","source_location":"table 1","excerpt":"SYNTHETIC measurement","actor":"synthetic demonstrator"}'
opentruth claim inspect --json '{"claim_id":"CLAIM_UUID"}'
opentruth history --json '{"claim_id":"CLAIM_UUID"}'
opentruth review --json '{"claim_id":"CLAIM_UUID","decision":"INCONCLUSIVE","reason":"Synthetic demonstration only","actor":"synthetic reviewer"}'
opentruth export > evidence.json
```

Expect NEEDS_REVIEW on creation, NOT_EVALUATED on sources, and
SUPPORTED_BY_REGISTERED_EVIDENCE only after the explicit support link.
