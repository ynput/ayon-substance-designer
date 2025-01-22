import os
import sd

from ayon_core.pipeline import publish
from ayon_substancedesigner.api.lib import get_sd_graph_by_name
from sd.api.sbs.sdsbsarexporter import SDSBSARExporter


class ExtractSbsar(publish.Extractor):
    """Extract SBSAR

    """

    label = "Extract SBSAR"
    hosts = ["substancedesigner"]
    families = ["sbsar"]

    order = publish.Extractor.order - 0.099

    def process(self, instance):
        ctx = sd.getContext()
        exporterInstance = SDSBSARExporter(ctx, None)
        exporter = exporterInstance.sNew()
        current_file = instance.context.data["currentFile"]
        filename = os.path.basename(current_file)
        filename = filename.replace("sbs", "sbsar")
        staging_dir = self.staging_dir(instance)
        sbsar_staging_dir = os.path.join(staging_dir, "sbsar")
        filepath = os.path.normpath(
            os.path.join(sbsar_staging_dir, filename))

        # export the graph with filepath
        exporter.exportSBSFileToSBSAR(current_file, filepath)

        representation = {
            'name': 'sbsar',
            'ext': 'sbsar',
            'files': filename,
            "stagingDir": sbsar_staging_dir,
        }

        instance.data["representations"].append(representation)
