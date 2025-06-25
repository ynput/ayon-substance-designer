from ayon_server.settings import (
    BaseSettingsModel,
    SettingsField,
    task_types_enum
)
from .imageio import ImageIOSettings, DEFAULT_IMAGEIO_SETTINGS


def template_workflow_enum():
    return [
        {"label": "Empty", "value": "empty"},
        {"label": "Metallic Roughness", "value": "metallic_roughness"},
        {"label": "Metallic Roughness - Anisotropy",
         "value": "metallic_roughness_anisotropy"},
        {"label": "Metallic Roughness - Coated",
         "value": "metallic_roughness_coated"},
        {"label": "Metallic Roughness - SSS",
         "value": "metallic_roughness_sss"},
        {"label": "Metallic Roughness - Sheen",
         "value": "metallic_roughness_sheen"},
        {"label": "Adobe Standard Material",
         "value": "adobe_standard_material"},
        {"label": "Specular Glossiness", "value": "specular_glossiness"},
        {"label": "Blinn", "value": "blinn"},
        {"label": "Scan Processing - Metallic Roughness",
         "value": "scan_metallic_roughness"},
        {"label": "Scan Processing - Specular Glossiness",
         "value": "scan_specular_glossiness"},
        {"label": "Scan Processing - Specular Glossiness",
         "value": "scan_specular_glossiness"},
        {"label": "AxF to Metallic Roughness",
         "value": "axf_to_metallic_roughness"},
        {"label": "AxF to Specular Glossiness",
         "value": "axf_to_specular_glossiness"},
        {"label": "AxF to AxF", "value": "axf_to_axf"},
        {"label": "Studio Panorama", "value": "studio_panorama"},
        {"label": "Painter Filter (generic)",
         "value": "sp_filter_generic"},
        {"label": "Painter Filter (specific)",
         "value": "sp_filter_specific"},
        {"label": "Painter Filter (specific w/ mesh maps)",
         "value": "sp_filter_channel_mesh_maps"},
        {"label": "Painter Generator (w/ mesh maps)",
         "value": "sp_generator_mesh_maps"},
        {"label": "Sample Filter", "value": "sample_filter"},
        {"label": "CLO Metallic Roughness",
         "value": "clo_metallic_roughness"},
    ]


def template_type_enum():
    return [
        {"label": "Default Substance Template",
         "value": "default_substance_template"},
        {"label": "Custom Template", "value": "custom_template"},
        {"label": "Template By Task Types", "value": "task_type_template"},
    ]


def document_resolution_enum():
    return [
        {"label": "2", "value": 1},
        {"label": "4", "value": 2},
        {"label": "8", "value": 3},
        {"label": "16", "value": 4},
        {"label": "32", "value": 5},
        {"label": "64", "value": 6},
        {"label": "128", "value": 7},
        {"label": "256", "value": 8},
        {"label": "512", "value": 9},
        {"label": "1024", "value": 10},
        {"label": "2048", "value": 11},
        {"label": "4096", "value": 12},
        {"label": "8192", "value": 13}
    ]


def image_format_enum():
    """Return enumerator for image output formats."""
    return [
        {"label": "bmp", "value": "bmp"},
        {"label": "dds", "value": "dds"},
        {"label": "jpeg", "value": "jpeg"},
        {"label": "png", "value": "png"},
        {"label": "tga", "value": "tga"},
        {"label": "tif", "value": "tif"},
        {"label": "surface", "value": "surface"},
        {"label": "hdr", "value": "hdr"},
        {"label": "exr", "value": "exr"},
        {"label": "jif", "value": "jif"},
        {"label": "jpe", "value": "jpe"},
        {"label": "webp", "value": "webp"},
    ]


class TaskTypeTemplateModel(BaseSettingsModel):
    _layout = "expanded"
    task_types: list[str] = SettingsField(
        default_factory=list,
        title="Task types",
        enum_resolver=task_types_enum
    )
    path: str = SettingsField("", title="Path to template")


class CustomTemplateModel(BaseSettingsModel):
    _layout = "expanded"
    custom_template_graph: str = SettingsField(
        "",
        title="Custom Template Graph Name",
        description=(
            "Name of the graph from the custom template"
            "you want to create your project from"
        )
    )
    custom_template_path: str = SettingsField(
        "",
        title="Path to Custom Template",
        description="Absolute path of which custom template located."

    )


class ProjectTemplatesModel(BaseSettingsModel):
    _layout = "expanded"
    grpah_name: str = SettingsField("default", title="Graph Name")
    default_texture_resolution: int = SettingsField(
        10, enum_resolver=document_resolution_enum,
        title="Document Resolution",
        description=("Set texture resolution when "
                     "creating new project.")
    )
    template_type: str = SettingsField(
        "default_substance_template",
        title="Template Type",
        description=("Choose either default substance templates "
                     "or custom template for project creation"),
        enum_resolver=template_type_enum,
        conditional_enum=True,
    )

    default_substance_template: str = SettingsField(
        "empty", enum_resolver=template_workflow_enum,
        title="Template",
        description=("Choose template to create your "
                     "Substance Graph.")
    )
    custom_template: CustomTemplateModel = SettingsField(
        title="Custom Template",
        description="What custom template to use for project creation",
        default_factory=CustomTemplateModel,
    )
    task_type_template: TaskTypeTemplateModel = SettingsField(
        title="Template By Task Type",
        description="Use task-type based template for project creation",
        default_factory=TaskTypeTemplateModel,
    )

class ProjectTemplateSettingModel(BaseSettingsModel):
    project_templates: list[ProjectTemplatesModel] = SettingsField(
        default_factory=ProjectTemplatesModel,
        title="Project Templates"
    )


class CreateTextureSettings(BaseSettingsModel):
    review : bool = SettingsField(False, title="Review")
    exportFileFormat: str = SettingsField(
        enum_resolver=image_format_enum,
        title="Image Output File Type")


class CreatePluginsModel(BaseSettingsModel):
    CreateTextures: CreateTextureSettings = SettingsField(
        default_factory=CreateTextureSettings,
        title="Create Textures"
    )


class SubstanceDesignerSettings(BaseSettingsModel):
    imageio: ImageIOSettings = SettingsField(
        default_factory=ImageIOSettings,
        title="Color Management (ImageIO)"
    )
    project_creation: ProjectTemplateSettingModel = SettingsField(
        default_factory=ProjectTemplateSettingModel,
        title="Project Creation"
    )
    create: CreatePluginsModel = SettingsField(
        default_factory=CreatePluginsModel,
        title="Creator Plugins"
    )

DEFAULT_SD_SETTINGS = {
    "imageio": DEFAULT_IMAGEIO_SETTINGS,
    "project_creation": {
        "project_templates": []
    },
    "create": {
        "CreateTextures": {
            "review": False,
            "exportFileFormat": "png"
        },
    }
}
