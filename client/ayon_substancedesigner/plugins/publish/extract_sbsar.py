import os
import sd

from ayon_core.pipeline import publish
from sd.api.sbs.sdsbsarexporter import SDSBSARExporter
from ayon_substancedesigner.api.lib import get_sd_graph_by_name


class ExtractSbsar(publish.Extractor):
    """Extract SBSAR

    """

    label = "Extract SBSAR"
    hosts = ["substancedesigner"]
    families = ["sbsar"]

    order = publish.Extractor.order

    def process(self, instance):
        ctx = sd.getContext()
        exporterInstance = SDSBSARExporter(ctx, None)
        exporter = exporterInstance.sNew()

        graph_name = instance.data["graph_name"]
        sd_graph = get_sd_graph_by_name(graph_name)

        current_file = instance.context.data["currentFile"]
        filename = os.path.basename(current_file)
        filename = filename.replace("sbs", "sbsar")
        staging_dir = self.staging_dir(instance)
        filepath = os.path.normpath(
            os.path.join(staging_dir, filename))
        # export the graph with filepath
        exporter.exportPackageToSBSAR(sd_graph.getPackage(), filepath)

        if "representations" not in instance.data:
            instance.data["representations"] = []
        representation = {
            'name': 'sbsar',
            'ext': 'sbsar',
            'files': filename,
            "stagingDir": staging_dir,
        }

        instance.data["representations"].append(representation)
