from __future__ import annotations

from effectdelta.adapters.base import ActionAdapter
from effectdelta.intent import estimate_intent_cardinality
from effectdelta.models import Action, EffectVector

_CHANNEL_ALIASES = {
    "editors": frozenset({"editors"}),
    "draft": frozenset({"editors"}),
    "subscribers": frozenset({"subscribers"}),
    "live": frozenset({"subscribers", "public"}),
    "public": frozenset({"public", "subscribers"}),
    "twitter": frozenset({"twitter"}),
    "x": frozenset({"twitter"}),
}


class MediaPublishAdapter(ActionAdapter):
    """Example media adapter — draft-to-editors vs live-to-everyone style checks."""

    kind = "media_publish"

    def intent_effect(self, action: Action) -> EffectVector:
        lower = action.intent.lower()
        channels = frozenset({"editors"})
        if "subscriber" in lower or "live" in lower or "public" in lower:
            channels = frozenset({"subscribers", "public"})
        cardinality = estimate_intent_cardinality(
            action.intent,
            default=10.0 if "editor" in lower or "draft" in lower else 1000.0,
        )
        if "editor" in lower or "draft" in lower:
            cardinality = float(action.payload.get("editor_count", 10))
        return EffectVector(
            cardinality=cardinality,
            targets=channels,
            irreversible="live" in lower or "public" in lower,
            resource_type="media_publish",
            sensitivity=0.7,
            channels=channels,
            environment=str(action.payload.get("environment", "prod")),
        )

    def proposed_effect(self, action: Action) -> EffectVector:
        raw_channels = action.payload.get("channels") or action.payload.get("channel") or []
        if isinstance(raw_channels, str):
            raw_channels = [raw_channels]
        channels: set[str] = set()
        for ch in raw_channels:
            key = str(ch).lower()
            channels |= set(_CHANNEL_ALIASES.get(key, {key}))

        audience = int(action.payload.get("audience_size", 0) or 0)
        if audience <= 0:
            if "subscribers" in channels or "public" in channels:
                audience = int(action.payload.get("subscriber_count", 50000))
            else:
                audience = int(action.payload.get("editor_count", 10))

        return EffectVector(
            cardinality=float(audience),
            targets=frozenset(channels) or frozenset({"unknown"}),
            irreversible=bool({"subscribers", "public"} & channels),
            resource_type="media_publish",
            sensitivity=0.9 if audience > 1000 else 0.5,
            channels=frozenset(channels),
            environment=str(action.payload.get("environment", "prod")),
            notes=("publish forecast — no content was pushed",),
        )
