from typing import Type

from ayon_server.addons import BaseServerAddon

from .settings import SubstanceDesignerSettings, DEFAULT_SD_VALUES


class SubstanceDesignerAddon(BaseServerAddon):
    settings_model: Type[SubstanceDesignerSettings] = SubstanceDesignerSettings

    async def get_default_settings(self):
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_SD_VALUES)
