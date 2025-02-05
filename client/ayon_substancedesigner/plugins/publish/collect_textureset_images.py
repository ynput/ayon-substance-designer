import copy

import pyblish.api
import ayon_api

from ayon_core.pipeline import tempdir

from ayon_core.pipeline.create import get_product_name
from ayon_substancedesigner.api.lib import (
    get_map_identifiers_by_graph,
    get_sd_graphs_by_package
)


class CollectTextureSet(pyblish.api.InstancePlugin):
    """Extract Textures using an output template config"""

    label = "Collect Texture Set images"
    hosts = ["substancedesigner"]
    families = ["textureSet"]
    order = pyblish.api.CollectorOrder + 0.01

    def process(self, instance):
        creator_attrs = instance.data["creator_attributes"]
        if creator_attrs.get("exportedGraphs", []):
            instance.data["exportedGraphs"] = creator_attrs.get(
                "exportedGraphs", [])
        else:
            instance.data["exportedGraph"] = get_sd_graphs_by_package()
        for graph_name in instance.data["exportedGraphs"]:
            map_identifiers = get_map_identifiers_by_graph(graph_name)
            project_name = instance.context.data["projectName"]
            folder_entity = ayon_api.get_folder_by_path(
                project_name,
                instance.data["folderPath"]
            )
            task_name = instance.data.get("task")
            task_entity = None
            if folder_entity and task_name:
                task_entity = ayon_api.get_task_by_name(
                    project_name, folder_entity["id"], task_name
                )
            staging_dir = tempdir.get_temp_dir(
                instance.context.data["projectName"],
                use_local_temp=True
            )
            instance.data["map_identifiers"] = map_identifiers

            for map_identifier in map_identifiers:
                self.create_image_instance(
                    instance, task_entity, graph_name,
                    map_identifier, staging_dir
                )

    def create_image_instance(self, instance,
                              task_entity, graph_name,
                              map_identifier, staging_dir):
        """Create a new instance per image.

        The new instances will be of product type `image`.

        """

        context = instance.context
        # Always include the map identifier
        texture_set_name = f"{graph_name}_{map_identifier}"

        task_name = task_type = None
        if task_entity:
            task_name = task_entity["name"]
            task_type = task_entity["taskType"]

        # TODO: The product type actually isn't 'texture' currently but
        #   for now this is only done so the product name starts with
        #   'texture'
        image_product_name = get_product_name(
            context.data["projectName"],
            task_name,
            task_type,
            context.data["hostName"],
            product_type="texture",
            variant=instance.data["variant"] + f"_{map_identifier}",
            project_settings=context.data["project_settings"]
        )
        image_product_group_name = get_product_name(
            context.data["projectName"],
            task_name,
            task_type,
            context.data["hostName"],
            product_type="texture",
            variant=instance.data["variant"],
            project_settings=context.data["project_settings"]
        )
        ext = instance.data["creator_attributes"].get("exportFileFormat")
        # Prepare representation
        representation = {
            "name": ext.lstrip("."),
            "ext": ext.lstrip("."),
            "files": f"{texture_set_name}.{ext}",
        }
        # Set up the representation for thumbnail generation
        representation["tags"] = ["review"]
        representation["stagingDir"] = staging_dir
        # Clone the instance
        product_type = "image"
        image_instance = context.create_instance(image_product_name)
        image_instance[:] = instance[:]
        image_instance.data.update(copy.deepcopy(dict(instance.data)))
        image_instance.data["name"] = image_product_name
        image_instance.data["label"] = image_product_name
        image_instance.data["productName"] = image_product_name
        image_instance.data["productType"] = product_type
        image_instance.data["family"] = product_type
        image_instance.data["families"] = [product_type, "textures"]
        if instance.data["creator_attributes"].get("review"):
            image_instance.data["families"].append("review")

        image_instance.data["representations"] = [representation]

        # Group the textures together in the loader
        image_instance.data["productGroup"] = image_product_group_name

        # Store the texture set name and stack name on the instance
        image_instance.data["textureSetName"] = texture_set_name

        # Store the instance in the original instance as a member
        instance.append(image_instance)


class CollectTextureSetStagingDir(pyblish.api.InstancePlugin):
    """Set the staging directory for the `textureSet` instance taking into
    account custom staging dirs. Propagate this custom staging dir to the
    individual texture image instances that are created from the textureSet"""

    label = "Texture Set Staging Dir"
    hosts = ["substancedesigner"]
    families = ["textureSet"]

    # Run after CollectManagedStagingDir
    order = pyblish.api.CollectorOrder + 0.4991

    def process(self, instance):

        staging_dir = instance.data["stagingDir"]
        # Update image instances and their representations
        for image_instance in instance:

            # Include the updated config
            image_instance.data["stagingDir"] = staging_dir

            # Update representation staging dir.
            for repre in image_instance.data["representations"]:
                repre["stagingDir"] = staging_dir
