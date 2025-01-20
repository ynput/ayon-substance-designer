import sd.tools.export as export
from ayon_core.pipeline import KnownPublishError, publish
from ayon_substancedesigner.api.lib import get_sd_graph_by_name



class ExtractTextures(publish.Extractor):
    """Extract Textures as Graph Outputs

    """

    label = "Extract Textures as Graph Outputs"
    hosts = ["substancedesigner"]
    families = ["textureSet"]

    # Run before thumbnail extractors
    order = publish.Extractor.order - 0.1

    def process(self, instance):
        graph_name = instance.data["graph_name"]
        target_sd_graph = get_sd_graph_by_name(graph_name)

        staging_dir = self.staging_dir(instance)
        extension = instance.data["exportFileFormat"]

        result = export.exportSDGraphOutputs(
            target_sd_graph, staging_dir, extension)
        if not result:
            raise KnownPublishError(
                "Failed to export texture output in graph: {}".format(
                    graph_name)
            )

        # The TextureSet instance should not be integrated. It generates no
        # output data. Instead the separated texture instances are generated
        # from it which themselves integrate into the database.
        instance.data["integrate"] = False
