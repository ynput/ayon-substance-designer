from ayon_server.settings import BaseSettingsModel, SettingsField
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


def document_resolution_enum():
    return [
        {"label": "16", "value": 16},
        {"label": "32", "value": 32},
        {"label": "64", "value": 32},
        {"label": "128", "value": 128},
        {"label": "256", "value": 256},
        {"label": "512", "value": 512},
        {"label": "1024", "value": 1024},
        {"label": "2048", "value": 2048},
        {"label": "4096", "value": 4096}
    ]


class ProjectTemplatesModel(BaseSettingsModel):
    _layout = "expanded"
    name: str = SettingsField("default", title="Template Name")
    default_texture_resolution: int = SettingsField(
        1024, enum_resolver=document_resolution_enum,
        title="Document Resolution",
        description=("Set texture resolution when "
                     "creating new project.")
    )
    project_workflow: str = SettingsField(
        "empty", enum_resolver=template_workflow_enum,
        title="Template",
        description=("Choose template to create your "
                     "Substance Graph.")
    )


class ProjectTemplateSettingModel(BaseSettingsModel):
    project_templates: list[ProjectTemplatesModel] = SettingsField(
        default_factory=ProjectTemplatesModel,
        title="Project Templates"
    )


class SubstanceDesignerSettings(BaseSettingsModel):
    imageio: ImageIOSettings = SettingsField(
        default_factory=ImageIOSettings,
        title="Color Management (ImageIO)"
    )
    DesignerProjectCreation: ProjectTemplateSettingModel = SettingsField(
        default_factory=ProjectTemplateSettingModel,
        title="Designer Project Creation"
    )


DEFAULT_SD_SETTINGS = {
    "imageio": DEFAULT_IMAGEIO_SETTINGS,
    "DesignerProjectCreation": {
        "project_templates": []
    }
}
