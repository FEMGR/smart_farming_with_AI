from app.services.knowledge.pest_service import normalize_pest


def test_normalize_pest_preserves_canonical_thrips():
    assert normalize_pest("thrips") == "thrips"
    assert normalize_pest("Thrip") == "thrips"


def test_normalize_pest_resolves_regular_plural_to_known_atom():
    assert normalize_pest("aphids") == "aphid"
    assert normalize_pest("spider mites") == "spider_mite"
    assert normalize_pest("flea beetles") == "flea_beetle"
