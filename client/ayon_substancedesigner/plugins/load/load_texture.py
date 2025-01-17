
from ayon_core.pipeline import (
    load
)
from ayon_substancedesigner.api.pipeline import imprint

class SubstanceLoadProjectImage(load.LoaderPlugin):
    """Load Image for project"""

    product_types = {"image", "textures"}
    representations = {"*"}

    label = "Load Image For Project Creation"
    order = -10
    icon = "code-fork"
    color = "orange"

    def load(self, context, name, namespace, options=None):
        pass

    def update(self, container, context):
        pass

    def remove(self, container):
        pass