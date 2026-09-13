from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["solutions"])

SOLUTIONS = {
    "personal": {
        "label": "What this app gives you today",
        "items": [
            {
                "title": "Advance risk calendar",
                "description": (
                    "Check the Risk Calendar before booking travel around any long weekend or "
                    "festival. HIGH/CRITICAL days come with a concrete departure-window and "
                    "corridor-avoidance recommendation derived from the Sep 11 2026 case study."
                ),
            },
            {
                "title": "Live corridor status",
                "description": (
                    "The dashboard polls real TomTom traffic data every ~15 minutes for the six "
                    "corridors named in this case study, so you can check current conditions "
                    "before leaving rather than after you're already stuck."
                ),
            },
            {
                "title": "Book and depart outside the 5PM-11PM exodus window",
                "description": (
                    "The single most actionable finding: gridlock consistently starts ~5PM and "
                    "runs past midnight on exodus evenings. Leaving before 2PM or after 11PM "
                    "avoids the worst of it entirely, evidenced directly in the case study."
                ),
            },
        ],
    },
    "systemic": {
        "label": "Systemic fixes only transit authorities/employers can implement",
        "items": [
            {
                "title": "Staggered holiday declarations by sector/region",
                "description": (
                    "Spreading the same festival's effective travel days across a wider window "
                    "(e.g. flexible holiday-adjacent leave for private sector) reduces the single-evening "
                    "demand spike that concentrates the exodus into a 3-4 hour window."
                ),
            },
            {
                "title": "Decentralized park-and-ride feeder shuttles",
                "description": (
                    "Private vehicles converging on Majestic/Shantinagar to drop passengers "
                    "compound congestion around the terminals themselves. Feeder shuttles from "
                    "outer-ring park-and-ride lots would keep that traffic off the core road network."
                ),
            },
            {
                "title": "Toll plaza throughput upgrades",
                "description": (
                    "Nelamangala, Kaniminike and Sheshagirihalli toll plazas were named as hard "
                    "bottlenecks independent of bus fleet size — more lanes and stricter FASTag "
                    "enforcement would raise the physical throughput ceiling at these exact points."
                ),
            },
            {
                "title": "Demand-anticipating bus scheduling",
                "description": (
                    "KSRTC's 2,400 extra buses were dispatched reactively. Ticket-search-volume-based "
                    "forecasting (a natural extension of this project's risk calendar) could trigger "
                    "capacity increases and public advisories 48-72 hours ahead instead."
                ),
            },
            {
                "title": "Advance public advisories via SMS/WhatsApp",
                "description": (
                    "A 24-48 hour advance push notification for HIGH/CRITICAL risk dates, using "
                    "exactly the data this project already computes, could shift some fraction of "
                    "departures earlier in the day voluntarily."
                ),
            },
        ],
    },
}


@router.get("/solutions")
def solutions() -> dict:
    return SOLUTIONS
