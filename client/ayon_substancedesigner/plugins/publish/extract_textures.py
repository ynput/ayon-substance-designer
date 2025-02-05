import os
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
        staging_dir = self.staging_dir(instance)
        extension = instance.data["creator_attributes"].get("exportFileFormat")
        map_identifiers = instance.data["map_identifiers"]

        for graph_name in instance.data["exportedGraphs"]:
            target_sd_graph = get_sd_graph_by_name(graph_name)
            result = export.exportSDGraphOutputs(
                target_sd_graph, staging_dir, extension)
            if not result:
                raise KnownPublishError(
                    "Failed to export texture output in graph: {}".format(
                        graph_name)
                )
            # Rename the directories accordingly to the output maps
            file_list_in_staging = [
                path for path in os.listdir(staging_dir) if os.path.isfile(
                    os.path.join(staging_dir, path))
            ]
            for file, identifier in zip(file_list_in_staging, map_identifiers):
                src = os.path.join(staging_dir, file)
                dst = os.path.join(staging_dir,
                                f"{graph_name}_{identifier}.{extension}")
                os.rename(src, dst)

            self.log.debug(f"Extracting to {staging_dir}")
        # The TextureSet instance should not be integrated. It generates no
        # output data. Instead the separated texture instances are generated
        # from it which themselves integrate into the database.
        instance.data["integrate"] = False
