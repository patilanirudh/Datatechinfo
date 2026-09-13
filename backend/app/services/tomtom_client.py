"""Thin client for TomTom's free-tier Traffic API.

Endpoint shapes verified against TomTom's public docs as of 2026-09-12:
- Flow Segment Data: https://docs.tomtom.com/traffic-api/documentation/tomtom-maps/v1/traffic-flow/flow-segment-data
- Incident Details:  https://docs.tomtom.com/traffic-api/documentation/tomtom-maps/v1/traffic-incidents/incident-details
- Geocoding:         https://developer.tomtom.com/search-api/documentation/search-service/geocoding

TomTom's API surface evolves; if either endpoint starts returning 4xx, check those
docs before assuming the road data itself is broken.
"""

from __future__ import annotations

from urllib.parse import quote

import httpx

FLOW_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
INCIDENTS_URL = "https://api.tomtom.com/traffic/services/5/incidentDetails"
GEOCODE_URL = "https://api.tomtom.com/search/2/geocode/{query}.json"
INCIDENT_FIELDS = (
    "{incidents{type,geometry{type,coordinates},"
    "properties{iconCategory,magnitudeOfDelay,events{description,code,iconCategory},"
    "startTime,endTime,from,to,length,delay,roadNumbers}}}"
)


class TomTomError(RuntimeError):
    pass


def fetch_flow_segment(lat: float, lon: float, api_key: str, timeout: float = 10.0) -> dict:
    """Return the raw flowSegmentData dict for the road segment nearest (lat, lon)."""
    params = {"point": f"{lat},{lon}", "key": api_key}
    resp = httpx.get(FLOW_URL, params=params, timeout=timeout)
    if resp.status_code != 200:
        raise TomTomError(f"flowSegmentData failed ({resp.status_code}): {resp.text[:200]}")
    data = resp.json()
    try:
        return data["flowSegmentData"]
    except KeyError as exc:
        raise TomTomError(f"Unexpected flowSegmentData response shape: {data}") from exc


def fetch_incidents(bbox: tuple[float, float, float, float], api_key: str, timeout: float = 10.0) -> list[dict]:
    """bbox = (min_lon, min_lat, max_lon, max_lat). Returns the list of incident features."""
    min_lon, min_lat, max_lon, max_lat = bbox
    params = {
        "key": api_key,
        "bbox": f"{min_lon},{min_lat},{max_lon},{max_lat}",
        "fields": INCIDENT_FIELDS,
        "language": "en-GB",
    }
    resp = httpx.get(INCIDENTS_URL, params=params, timeout=timeout)
    if resp.status_code != 200:
        raise TomTomError(f"incidentDetails failed ({resp.status_code}): {resp.text[:200]}")
    data = resp.json()
    return data.get("incidents", [])


def geocode(query: str, api_key: str, timeout: float = 10.0) -> dict | None:
    """Resolve a free-text place name to its best-match address + (lat, lon).
    Returns None if nothing matched, rather than raising — an empty search result
    isn't an error condition the caller needs to treat differently from a 200."""
    url = GEOCODE_URL.format(query=quote(query))
    params = {"key": api_key, "limit": 1}
    resp = httpx.get(url, params=params, timeout=timeout)
    if resp.status_code != 200:
        raise TomTomError(f"geocode failed ({resp.status_code}): {resp.text[:200]}")
    results = resp.json().get("results", [])
    if not results:
        return None
    best = results[0]
    return {
        "freeform_address": best["address"]["freeformAddress"],
        "lat": best["position"]["lat"],
        "lon": best["position"]["lon"],
    }
