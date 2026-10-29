# Optional scientific context checklists

Templates suggest fields without claiming that a study or measurement is scientifically complete.
They do not fill in unknown facts, choose units, or infer experimental equivalence.

```sh
opentruth context templates
opentruth context templates engineering
opentruth --format text claim add "SYNTHETIC: beam length is 1 m." --subject beam --predicate length --value 1 --unit m --context-template engineering --context '{"method":"synthetic caliper"}'
```

| Template | Suggested fields |
|---|---|
| engineering | method, conditions, instrument, time |
| experiment | method, conditions, sample, time |
| study | population, method, time, geographic_scope |

Supply a template with `context_template` in the Python API, JSON CLI, or MCP `add_claim` tool.
The actual `context` remains an extensible dictionary. Claim creation, revision, and inspection
return `context_warnings` for absent, null, blank, or empty required values. Recording a claim
with missing fields is allowed; warnings do not silently invent context.

Deterministic comparison refuses incomplete template contexts or different selected templates,
even when the populated fields match. Complete matching contexts only satisfy this declared-field
policy; they do not establish that all relevant confounders have been captured. Even without a
template, explicitly empty context values prevent numerical comparison. Add further domain-specific
attributes when necessary; different context dictionaries remain insufficiently comparable.

Legacy claims have no template selected and remain readable/revisable without migration.
