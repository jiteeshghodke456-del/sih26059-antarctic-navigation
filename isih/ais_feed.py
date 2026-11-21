"""AIS target feed for the traffic gate (HANDOFF_TONIGHT slice 8).

Decodes NMEA 0183 AIS sentences with pyais (MIT) from the sources a ship
actually has: its own AIS receiver on a UDP or TCP port (the normal NMEA
output path), or a recorded NMEA file. Keeps the latest position per MMSI.

Shore-network reality, written down so nobody oversells it: terrestrial
aggregators such as aisstream.io reach ~40 nm from coastal receivers and are
EMPTY in the Southern Ocean. Satellite AIS is paid. The ship's own receiver
is the only free source down there — which is why this module speaks NMEA
first and treats any network feed as an optional extra. With no live feed the
traffic gate stays UNKNOWN; it never pretends.
"""
from __future__ import annotations

import datetime as dt
import socket
from dataclasses import dataclass
from pathlib import Path

from pyais import decode


@dataclass
class Target:
    mmsi: int
    lat: float
    lon: float
    sog_kn: float | None
    cog_deg: float | None
    seen: dt.datetime


class AISFeed:
    """Latest known position per MMSI, fed one NMEA sentence at a time."""

    def __init__(self):
        self.targets: dict[int, Target] = {}
        self._fragments: list[bytes] = []

    def feed_sentence(self, raw: bytes | str) -> Target | None:
        """Decode one sentence (handles multi-fragment messages). Returns the
        updated target when the sentence completed a position report."""
        if isinstance(raw, str):
            raw = raw.encode()
        raw = raw.strip()
        if not raw or not raw.startswith((b"!", b"$")):
            return None
        # NMEA field 2 is the fragment count: buffer only genuine multi-part
        # sentences, so garbage can never poison the fragment buffer.
        fields = raw.split(b",")
        n_frag = fields[1] if len(fields) > 2 else b"1"
        try:
            if n_frag != b"1":
                self._fragments.append(raw)
                if fields[2] != n_frag:        # not the last fragment yet
                    return None
                msg = decode(*self._fragments)
                self._fragments = []
            else:
                msg = decode(raw)
        except Exception:
            self._fragments = []
            return None
        lat = getattr(msg, "lat", None)
        lon = getattr(msg, "lon", None)
        if lat is None or lon is None:
            return None
        t = Target(
            mmsi=int(msg.mmsi),
            lat=float(lat), lon=float(lon),
            sog_kn=float(msg.speed) if getattr(msg, "speed", None) is not None else None,
            cog_deg=float(msg.course) if getattr(msg, "course", None) is not None else None,
            seen=dt.datetime.now(dt.timezone.utc),
        )
        self.targets[t.mmsi] = t
        return t

    def feed_file(self, path: Path | str) -> int:
        """Read a recorded NMEA log. Returns the number of position updates."""
        n = 0
        for line in Path(path).read_bytes().splitlines():
            if self.feed_sentence(line) is not None:
                n += 1
        return n

    def listen_udp(self, port: int, host: str = "0.0.0.0",
                   duration_s: float = 10.0) -> int:
        """Collect from a UDP NMEA stream (the common receiver output)."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.0)
        sock.bind((host, port))
        end = dt.datetime.now() + dt.timedelta(seconds=duration_s)
        n = 0
        try:
            while dt.datetime.now() < end:
                try:
                    data, _ = sock.recvfrom(4096)
                except socket.timeout:
                    continue
                for line in data.splitlines():
                    if self.feed_sentence(line) is not None:
                        n += 1
        finally:
            sock.close()
        return n
