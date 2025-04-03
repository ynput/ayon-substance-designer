import os
import sd
from ayon_core.pipeline import load

from ayon_core.lib import EnumDef
from ayon_substancedesigner.api.pipeline import (
    imprint,
    remove_container_metadata
)
from ayon_substancedesigner.api.lib import get_package_from_current_graph


def has_resource_file(current_package):
    for resource in current_package.getChildrenResources(True):
        if resource.getClassName() == "SDResourceFolder":
            return True
    return False


def get_resource_folder(current_package):
    for resource in current_package.getChildrenResources(True):
        if resource.getClassName() == "SDResourceFolder":
            return resource


class SubstanceLoadProjectImage(load.LoaderPlugin):
    """Load Texture for project"""

    product_types = {"image", "textures"}
    representations = {"*"}

    label = "Load Texture"
    order = -10
    icon = "code-fork"
    color = "orange"


    @classmethod
    def get_options(cls, contexts):
        return [
            EnumDef(
                    "resource_loading_options",
                    label="Resource Loading Options",
                    items={
                        1: "Linked",
                        2: "CopiedAndLinked",
                        3: "BinaryEmbedded",
                    },
                    default=1
            ),
        ]

    def load(self, context, name, namespace, options):
        current_package = get_package_from_current_graph()
        filepath = self.filepath_from_context(context)
        resource_embed_method = options.get("resource_loading_options", 1)
        import_options = {
            "resource_loading_options": resource_embed_method
        }
        identifier = self.import_texture(
            filepath, context, current_package, resource_embed_method)
        imprint(
            current_package, name, namespace,
            context, loader=self, identifier=identifier,
            options=import_options
        )

    def update(self, container, context):
        # As the filepath for SD Resource file is read-only data.
        # the update function cannot directly set the textures
        # accordingly to the versions in the existing SD Resource
        # Therefore, new resource version of the bitmap would be
        # created when updating
        current_package = get_package_from_current_graph()
        filepath = self.filepath_from_context(context)
        resource_embed_method = int(container["resource_loading_options"])
        options = {
            "resource_loading_options": resource_embed_method
        }
        identifier = self.import_texture(
            filepath, context, current_package, resource_embed_method)
        imprint(
            current_package,
            container["name"],
            container.get("namespace", None),
            context,
            loader=self,
            identifier=identifier,
            options=options
        )

    def remove(self, container):
        # TODO: Supports the check across different packages if needed
        current_package = get_package_from_current_graph()
        for resource in current_package.getChildrenResources(True):
            if resource.getClassName() == "SDResourceBitmap":
                if resource.getIdentifier() == container["objectName"]:
                    resource.delete()
        remove_container_metadata(container)

    def import_texture(self, filepath, context,
                       current_package, resource_embed_method):
        """Import textures as Substance Designer Package

        Args:
            filepath (str): filepath
            context (dict): context
            current_package (sd.api.sdpackage.SDPackage): current Substance
                package
            resource_embed_method (str): Resource emebed method

        Returns:
            str: Map identifier
        """
        project_name = context["project"]["name"]
        filename = os.path.splitext(os.path.basename(filepath))[0]
        # identifier would convert "." to "_", this makes sure
        # container data taking correct identifier value
        identifier = filename.replace(".", "_")
        if not has_resource_file(current_package):
            resource_folder = sd.api.sdresourcefolder.SDResourceFolder.sNew(
                current_package)
            resource_folder.setIdentifier(f"{project_name}_resources")
        else:
            resource_folder = get_resource_folder(current_package)
        bitmap_resource = sd.api.sdresourcebitmap.SDResourceBitmap.sNewFromFile(                # noqa
            resource_folder, filepath,
            sd.api.sdresource.EmbedMethod(resource_embed_method)
        )
        bitmap_resource.setIdentifier(identifier)

        return identifier
