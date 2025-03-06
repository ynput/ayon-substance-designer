# -*- coding: utf-8 -*-
"""Creator plugin for creating textures."""
from ayon_core.pipeline import CreatorError
from ayon_core.lib import BoolDef, EnumDef

from ayon_substancedesigner.api.pipeline import set_instance
from ayon_substancedesigner.api.lib import (
    get_current_graph_name,
    get_sd_graphs_by_package,
    get_output_maps_from_graphs
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

    def get_dynamic_data(
        self,
        project_name,
        folder_entity,
        task_entity,
        variant,
        host_name,
        instance
    ):
        """
        The default product name templates for Unreal include {asset} and thus
        we should pass that along as dynamic data.
        """
        dynamic_data = super(CreateTextures, self).get_dynamic_data(
            project_name,
            folder_entity,
            task_entity,
            variant,
            host_name,
            instance
        )
        dynamic_data["asset"] = folder_entity["name"]
        return dynamic_data

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
            "exportedGraphs",
            "exportedGraphsOutputs"
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
                    multiselection=True,
                    default=None,
                    label="Graphs To be Exported"),
            EnumDef("exportedGraphsOutputs",
                    items=get_output_maps_from_graphs(),
                    multiselection=True,
                    default=None,
                    label="Graph Outputs To be Exported")
        ]
