"""
Image repository.

All Image data access goes through here. Currently delegates to the stub
data source; swap for SQLAlchemy queries without touching routes or templates.
"""

from typing import List, Optional

from models.image import Image
from services import image_stub_data


class ImageRepository:
    """All Image DB access goes through here."""

    # ------------------------------------------------------------------
    # Read methods
    # ------------------------------------------------------------------

    @staticmethod
    def list_all(limit: Optional[int] = None) -> List[Image]:
        """
        Return all gallery images in random order.

        FUTURE (SQLAlchemy):
            from sqlalchemy import func
            q = Image.query.order_by(func.random())
            return q.limit(limit).all() if limit else q.all()
        """
        images = image_stub_data.get_all_images_stub(shuffle=True)
        return images[:limit] if limit is not None else images

    @staticmethod
    def get_by_id(image_id: int) -> Optional[Image]:
        """
        Single-image lookup. Returns None if not found.

        FUTURE (SQLAlchemy):
            return Image.query.get(image_id)
        """
        return image_stub_data.get_image_by_id_stub(image_id)

    # ------------------------------------------------------------------
    # Write methods – placeholders until the DB layer is live.
    # ------------------------------------------------------------------

    @staticmethod
    def create(filename: str, title: str) -> Image:
        """Register an uploaded image. NotImplemented until DB is wired up."""
        raise NotImplementedError("ImageRepository.create needs the DB layer")

    @staticmethod
    def delete(image_id: int) -> bool:
        """Delete by id. Returns True on success."""
        raise NotImplementedError("ImageRepository.delete needs the DB layer")
