# -*- coding: utf-8 -*-
"""Creator plugin for creating textures."""
from ayon_core.pipeline import CreatorError
from ayon_core.lib import BoolDef, EnumDef

from ayon_substancedesigner.api.pipeline import set_instance
from ayon_substancedesigner.api.lib import (
    get_current_graph_name,
    get_sd_graphs_by_package
)
from ayon_substancedesigner.api.plugin import TextureCreator


class CreateTextures(TextureCreator):
    """Create a texture set."""
    identifier = "io.ayon.creators.substancedesigner.textureset"
    label = "Textures"
    product_type = "textureSet"
    icon = "picture-o"

    default_variant = "Main"
    settings_category = "substancedesigner"
    review = False
    exportFileFormat = "png"

    def apply_settings(self, project_settings):
        texture_settings = project_settings["substancedesigner"].get(
            "create_texture", {})
        if texture_settings:
            self.review = texture_settings.get("review", False)
            self.exportFileFormat = texture_settings.get(
                "exportFileFormat", "png")

    def create(self, product_name, instance_data, pre_create_data):
        current_graph_name = get_current_graph_name()
        if not current_graph_name:
            raise CreatorError("Can't create a Texture Set instance without "
                               "the Substance Designer Graph.")
        # Transfer settings from pre create to instance
        creator_attributes = instance_data.setdefault(
            "creator_attributes", dict())
        for key in [
            "review",
            "exportFileFormat",
            "exportedGraphs"
        ]:
            if key in pre_create_data:
                creator_attributes[key] = pre_create_data[key]

        instance = self.create_instance_in_context(product_name,
                                                   instance_data)
        set_instance(
            instance_id=instance["instance_id"],
            instance_data=instance.data_to_store()
        )

    def get_instance_attr_defs(self):
        return [
            BoolDef("review",
                    label="Review",
                    tooltip="Mark as reviewable",
                    default=self.review),
            EnumDef("exportFileFormat",
                    items={
                        # TODO: Get available extensions from substance API
                        "bmp": "bmp",
                        "dds": "dds",
                        "jpeg": "jpeg",
                        "jpg": "jpg",
                        "png": "png",
                        "tga": "targa",
                        "tif": "tiff",
                        "surface": "surface",
                        "hdr": "hdr",
                        "exr": "exr",
                        "jif": "jif",
                        "jpe": "jpe",
                        "webp": "webp",
                        # TODO: File formats that combine the exported textures
                        #   like psd are not correctly supported due to
                        #   publishing only a single file
                        # "sbsar": "sbsar",
                    },
                    default=self.exportFileFormat,
                    label="File type"),
            EnumDef("exportedGraphs",
                    items=get_sd_graphs_by_package(),
                    default=None,
                    label="Graphs To be Exported")
        ]
