"""Public operations; pass an OpenTruth engine as the first argument."""

from .engine import OpenTruth

add_claim = OpenTruth.add_claim
revise_claim = OpenTruth.revise_claim
search_claims = OpenTruth.search_claims
inspect_claim = OpenTruth.inspect_claim
review_claim = OpenTruth.review_claim
