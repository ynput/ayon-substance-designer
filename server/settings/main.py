from ayon_server.settings import BaseSettingsModel, SettingsField
from .imageio import ImageIOSettings, DEFAULT_IMAGEIO_SETTINGS


def image_format_enum():
    """Return enumerator for image output formats."""
    return [
        {"label": "bmp", "value": "bmp"},
        {"label": "dds", "value": "dds"},
        {"label": "jpeg", "value": "jpeg"},
        {"label": "png", "value": "png"},
        {"label": "tga", "value": "tga"},
        {"label": "tif", "value": "tif"},
        {"label": "surface", "value": "surface"},
        {"label": "hdr", "value": "hdr"},
        {"label": "exr", "value": "exr"},
        {"label": "jif", "value": "jif"},
        {"label": "jpe", "value": "jpe"},
        {"label": "webp", "value": "webp"},
    ]


class CreateTextureSettings(BaseSettingsModel):
    review : bool = SettingsField(False, title="Review")
    exportFileFormat: str = SettingsField(
        enum_resolver=image_format_enum,
        title="Image Output File Type")

class SubstanceDesignerSettings(BaseSettingsModel):
    imageio: ImageIOSettings = SettingsField(
        default_factory=ImageIOSettings,
        title="Color Management (ImageIO)"
    )
    create_texture: CreateTextureSettings = SettingsField(
        default_factory=CreateTextureSettings,
        title="Create Textures"
    )


DEFAULT_SD_SETTINGS = {
    "imageio": DEFAULT_IMAGEIO_SETTINGS,
    "create_texture": {
        "review": False,
        "exportFileFormat": "png"
    }
}
