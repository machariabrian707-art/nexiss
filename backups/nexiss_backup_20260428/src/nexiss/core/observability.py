from __future__ import annotations

from nexiss.core.config import get_settings

settings = get_settings()


def configure_observability() -> None:
    if settings.observability_provider == "disabled":
        return
    if settings.observability_provider == "sentry":
        if not settings.sentry_dsn:
            raise RuntimeError("SENTRY_DSN is required when OBSERVABILITY_PROVIDER=sentry")
        try:
            import sentry_sdk  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError("sentry-sdk not installed. Install the 'sentry-sdk' package.") from exc

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=0.0,
        )
        return

    raise ValueError(f"Unsupported observability provider: {settings.observability_provider}")

