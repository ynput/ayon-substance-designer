from ayon_core.pipeline import KnownPublishError, publish
from ayon_substancedesigner.api.lib import (
    get_sd_graph_by_name,
    export_outputs_by_sd_graph
)


class ExtractTextures(publish.Extractor):
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
        # The TextureSet instance should not be integrated. It generates no
        # output data. Instead the separated texture instances are generated
        # from it which themselves integrate into the database.
        instance.data["integrate"] = False
