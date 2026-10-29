"""Optional context checklists, not validated scientific protocols."""

TEMPLATES = {
    "engineering": {
        "description": "Measurement conditions for a synthetic engineering observation",
        "fields": ["method", "conditions", "instrument", "time"],
    },
    "experiment": {
        "description": "Experimental conditions; adapt to the relevant scientific domain",
        "fields": ["method", "conditions", "sample", "time"],
    },
    "study": {
        "description": "Study population and scope; not a guarantee against confounding",
        "fields": ["population", "method", "time", "geographic_scope"],
    },
}


def context_warnings(context, template=None):
    required = TEMPLATES[template]["fields"] if template else list(context)
    return [
        f"Missing context field: {field}"
        for field in required
        if field not in context
        or context[field] is None
        or (isinstance(context[field], str) and not context[field].strip())
        or context[field] == {}
        or context[field] == []
    ]
