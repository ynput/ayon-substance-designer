from ayon_core.pipeline import KnownPublishError, publish
from ayon_substancedesigner.api.lib import (
    get_sd_graph_by_name,
    export_outputs_by_sd_graph
)


class ExtractTextures(publish.Extractor,
                      publish.ColormanagedPyblishPluginMixin):
    """Extract Textures as Graph Outputs

    """

    label = "Extract Textures as Graph Outputs"
    hosts = ["substancedesigner"]
    families = ["textureSet"]

    # Run before thumbnail extractors
    order = publish.Extractor.order - 0.1

    def process(self, instance):
        staging_dir = self.staging_dir(instance)
        extension = instance.data["creator_attributes"].get("exportFileFormat")

        for graph_name in instance.data["exportedGraphs"]:
            selected_map_identifiers = instance.data[graph_name].get(
                "map_identifiers", {})
            target_sd_graph = get_sd_graph_by_name(graph_name)
            result = export_outputs_by_sd_graph(
                instance.name, target_sd_graph,
                staging_dir, extension,
                selected_map_identifiers
            )
            if not result:
                raise KnownPublishError(
                    "Failed to export texture output in graph: {}".format(
                        graph_name)
                )

            self.log.debug(f"Extracting to {staging_dir}")
        # We'll insert the color space data for each image instance that we
        # added into this texture set. The collector couldn't do so because
        # some anatomy and other instance data needs to be collected prior
        context = instance.context
        for image_instance in instance:
            representation = next(iter(image_instance.data["representations"]))

            colorspace = image_instance.data.get("colorspace")
            if not colorspace:
                self.log.debug("No color space data present for instance: "
                               f"{image_instance}")
                continue

            self.set_representation_colorspace(representation,
                                               context=context,
                                               colorspace=colorspace)
        # The TextureSet instance should not be integrated. It generates no
        # output data. Instead the separated texture instances are generated
        # from it which themselves integrate into the database.
        instance.data["integrate"] = False
