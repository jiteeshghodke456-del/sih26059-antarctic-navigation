"""Slice 8 check: sample NMEA sentences from the pyais documentation decode to
targets with positions; garbage is rejected without state corruption."""
from ais_feed import AISFeed

# Single-fragment type 1 position report, from the pyais README examples.
SINGLE = b"!AIVDM,1,1,,B,15M67FC000G?ufbE`FepT@3n00Sa,0*5C"
# Two-fragment type 5 (static voyage data, no position) — exercises buffering.
MULTI = [
    b"!AIVDM,2,1,4,A,55O0W7`00001L@gCWGA2uItLth@DqtL5@F22220j1h742t0Ht0000000,0*08",
    b"!AIVDM,2,2,4,A,000000000000000,2*20",
]


def test_position_report_decodes_to_target():
    feed = AISFeed()
    t = feed.feed_sentence(SINGLE)
    assert t is not None
    assert t.mmsi > 0
    assert -90 <= t.lat <= 90 and -180 <= t.lon <= 180
    assert feed.targets[t.mmsi] is t


def test_multi_fragment_and_non_position_messages():
    feed = AISFeed()
    assert feed.feed_sentence(MULTI[0]) is None   # buffered, incomplete
    out = feed.feed_sentence(MULTI[1])            # completes but has no position
    assert out is None
    assert feed._fragments == []                  # buffer was consumed


def test_garbage_is_rejected():
    feed = AISFeed()
    assert feed.feed_sentence(b"not nmea at all") is None
    assert feed.feed_sentence(b"") is None
    assert feed.feed_sentence(SINGLE) is not None  # still works afterwards


def test_hostile_fragments_cannot_grow_the_buffer():
    feed = AISFeed()
    # absurd fragment count, out-of-order numbers, non-numeric fields
    assert feed.feed_sentence(b"!AIVDM,99,1,4,A,xxxx,0*00") is None
    assert feed.feed_sentence(b"!AIVDM,2,2,4,A,yyyy,2*20") is None  # no first part
    assert feed.feed_sentence(b"!AIVDM,abc,def,4,A,zzzz,0*00") is None
    assert feed._fragments == []
    assert feed.feed_sentence(SINGLE) is not None
