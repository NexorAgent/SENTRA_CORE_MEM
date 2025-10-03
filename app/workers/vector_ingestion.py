from __future__ import annotations

import asyncio
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def run_worker() -> None:
    settings = get_settings()
    logger.info(
        "Vector ingestion worker initialised",
        extra={
            "embedding_model": settings.embedding_model_name,
            "dimension": settings.embedding_vector_dimension,
        },
    )
    while True:
        await asyncio.sleep(300)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:  # pragma: no cover - manual stop
        logger.info("Vector ingestion worker stopped")


if __name__ == "__main__":
    main()
