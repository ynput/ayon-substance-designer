import copy

import pyblish.api

from ayon_core.pipeline import tempdir
from ayon_core.pipeline.publish import KnownPublishError

from ayon_substancedesigner.api.lib import (
    get_map_identifiers_by_graph,
    get_sd_graphs_by_package,
    get_colorspace_data
)


class CollectTextureSet(pyblish.api.InstancePlugin):
    """Extract Textures using an output template config"""

    label = "Collect Texture Set images"
    hosts = ["substancedesigner"]
    families = ["textureSet"]
    order = pyblish.api.CollectorOrder + 0.01

    def process(self, instance):
        staging_dir = tempdir.get_temp_dir(
            instance.context.data["projectName"],
            use_local_temp=True
        )
        creator_attrs = instance.data["creator_attributes"]
        if creator_attrs.get("exportedGraphs", []):
            instance.data["exportedGraphs"] = creator_attrs.get(
                "exportedGraphs", [])
        else:
            instance.data["exportedGraphs"] = get_sd_graphs_by_package()

        selected_map_identifiers = creator_attrs.get(
            "exportedGraphsOutputs", {})
        for graph_name in instance.data["exportedGraphs"]:
            map_identifiers = get_map_identifiers_by_graph(graph_name)
            if not map_identifiers:
                continue
            if selected_map_identifiers:
                map_identifiers = map_identifiers.intersection(
                    selected_map_identifiers
                )
                if not map_identifiers:
                    raise KnownPublishError(
                        f"Selected output maps {selected_map_identifiers}"
                        f"not found in the graph: {graph_name}"
                    )

            instance.data[graph_name] = {
                "map_identifiers": map_identifiers
            }

            for map_identifier in map_identifiers:
                self.create_image_instance(
                    instance, graph_name,
                    map_identifier, staging_dir
                )

    def create_image_instance(self, instance, graph_name,
                              map_identifier, staging_dir):
        """Create a new instance per image.

        The new instances will be of product type `image`.

        """

        context = instance.context
        # Always include the map identifier
        texture_set_name = f"{graph_name}_{map_identifier}"

        # TODO: The product type actually isn't 'texture' currently but
        #   for now this is only done so the product name starts with
        #   'texture'
        image_product_name = f"{instance.name}_{texture_set_name}"
        image_product_group_name = f"{instance.name}_{graph_name}"
        ext = instance.data["creator_attributes"].get("exportFileFormat")
        # Prepare representation
        representation = {
            "name": ext.lstrip("."),
            "ext": ext.lstrip("."),
            "files": f"{image_product_name}.{ext}",
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

        # The current api does not support to get colorspace data
        # from the output so the colorspace setting is hardcoded for
        # the colorspace data accordingly to the default output setting
        if map_identifier in ["diffuse", "basecolor"]:
            colorspace = get_colorspace_data()
        else:
            colorspace = get_colorspace_data(raw_colorspace=True)

        self.log.debug(f"{image_product_name} colorspace: {colorspace}")
        image_instance.data["colorspace"] = colorspace

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
