from ayon_server.settings import BaseSettingsModel, SettingsField
from .imageio import ImageIOSettings, DEFAULT_IMAGEIO_SETTINGS


class SubstanceDesignerSettings(BaseSettingsModel):
    imageio: ImageIOSettings = SettingsField(
        default_factory=ImageIOSettings,
        title="Color Management (ImageIO)"
    )


DEFAULT_SD_SETTINGS = {
    "imageio": DEFAULT_IMAGEIO_SETTINGS,
}
