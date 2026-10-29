"""Public operations; pass an OpenTruth engine as the first argument."""

from .engine import OpenTruth

register_source = OpenTruth.register_source
verify_sources = OpenTruth.verify_sources
