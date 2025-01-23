import os
import sd

from ayon_core.pipeline import publish
from sd.api.sbs.sdsbsarexporter import SDSBSARExporter


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
        current_file = instance.context.data["currentFile"]
        filename = os.path.basename(current_file)
        filename = filename.replace("sbs", "sbsar")
        staging_dir = self.staging_dir(instance)
        filepath = os.path.normpath(
            os.path.join(staging_dir, filename))
        exporter.exportSBSFileToSBSAR(current_file, filepath)

        if "representations" not in instance.data:
            instance.data["representations"] = []
        representation = {
            'name': 'sbsar',
            'ext': 'sbsar',
            'files': filename,
            "stagingDir": staging_dir,
        }

        instance.data["representations"].append(representation)
