from src.entities.exceptions.works import WorkImageTooSmallError

MIN_WORK_IMAGE_WIDTH = 200
MIN_WORK_IMAGE_HEIGHT = 300


def validate_work_image_dimensions(width: int, height: int) -> None:
    """Both displayed dimensions must meet the inclusive artwork minimum."""
    if width < MIN_WORK_IMAGE_WIDTH or height < MIN_WORK_IMAGE_HEIGHT:
        raise WorkImageTooSmallError
