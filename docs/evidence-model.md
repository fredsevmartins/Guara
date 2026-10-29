# Evidence model

A source does not support a claim merely because it exists. `link_evidence` requires an explicit
SUPPORTS, CONTRADICTS, RELATED, or INCONCLUSIVE relationship, source location, excerpt, and actor.
Every link starts NEEDS_REVIEW. Revising its interpretation retains the previous link in an event.
Source identity/endpoints are immutable; register a new source or link to change them.

Links record the claim's `claim_revision` number. Inspection returns every historical link with
`applies_to_current_revision`; only assessments of the current revision contribute to its evidence
summary. Revising a claim therefore resets its summary to INSUFFICIENT_EVIDENCE until evidence is
explicitly reassessed with `revise_evidence` or newly linked. Old excerpts and assessments remain
in history. A revision of a link applies the new assessment to the current claim revision.
Legacy links without a revision number are conservatively treated as assessments of revision 1;
review them explicitly if they were originally made against a later revision.

`inspect_claim` summarizes registered links as SUPPORTED_BY_REGISTERED_EVIDENCE,
CONTRADICTED_BY_REGISTERED_EVIDENCE, CONFLICTING_REGISTERED_EVIDENCE, or INSUFFICIENT_EVIDENCE.
This summary counts relationship labels, not evidence quality or independence. It does not weight
reviews or evaluate source content. Source verification remains NOT_EVALUATED; SHA-256 checks
copied bytes during registration, not the validity of their scientific content.
