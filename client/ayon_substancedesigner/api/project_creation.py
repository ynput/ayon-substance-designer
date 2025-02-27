# -*- coding: utf-8 -*-
import os
import sd
import errno
import logging
import ayon_api
import xml.etree.ElementTree as etree

from sd.api.sdapplication import SDApplicationPath
from sd.api.sdproperty import (
    SDPropertyCategory,
    SDPropertyInheritanceMethod
)
from sd.api.sdvalueint2 import SDValueInt2
from sd.api.sdbasetypes import int2

from ayon_core.pipeline import (
    tempdir,
    get_current_project_name,
    get_current_folder_path,
    get_current_task_name
)
from ayon_core.settings import get_current_project_settings
from ayon_substancedesigner.api.lib import get_sd_graph_by_name


log = logging.getLogger("ayon_substancedesigner")


def parse_graph_from_template(graph_name, project_template, template_filepath):
    """Parse graph by project template name from Substance template file
    Args:
        graph_name (str): graph_name
        project_template (str): project template name
        template_filepath (str): Substance template filepath

    """
    # Parse the template substance file
    substance_tree = etree.parse(template_filepath)
    substance_root = substance_tree.getroot()

    # Find the <graph> element with the specified identifier
    graph_element = None
    for graph in substance_root.findall('.//graph'):
        identifier = graph.find('identifier')
        if identifier is not None and (
            identifier.attrib.get('v') == project_template
            ):
                graph_element = graph
                break

    if graph_element is None:
        log.warning(
            f"Graph with identifier '{project_template}' "
            f"not found in {template_filepath}."
        )
        exit()

    identifier_element = graph_element.find('identifier')
    if identifier.attrib.get('v') == project_template:
        identifier_element.attrib['v'] = graph_name
    return graph_element


def add_graphs_to_package(parsed_graph_names, temp_package_filepath):
    """Add graphs to the temp package

    Args:
        temp_package_filepath (str): temp package filepath

    """
    # Parse the temp package file
    unsaved_tree = etree.parse(temp_package_filepath)
    unsaved_root = unsaved_tree.getroot()

    # Find the <content> element in Unsaved_Package.xml
    content_element = unsaved_root.find('content')

    # Remove the existing <content/> element if it exists
    if content_element is not None:
        unsaved_root.remove(content_element)
    # Create a new <content> element and append the copied <graph> element
    new_content = etree.Element('content')
    new_content.extend(parsed_graph_names)  # Append the copied <graph> element
    unsaved_root.append(new_content)   # Add the new <content> to the root
    # Save the modified content for Substance file
    unsaved_tree.write(
        temp_package_filepath,
        encoding='utf-8',
        xml_declaration=True
    )

    log.warning("All graphs are copied and pasted successfully!")


def create_tmp_package_for_template(sd_pkg_mgr, project_name):
    """Create temp substance package for template graph

    Args:
        sd_pkg_mgr (sd.api.sdpackagemgr.SDPackageMgr): package manager
        project_name (str): project_name

    Returns:
        sd.api.sdpackage.SDPackage, str: SD Package and template file path

    """
    temp_package = sd_pkg_mgr.newUserPackage()
    staging_dir = tempdir.get_temp_dir(
        project_name, use_local_temp=True
    )
    path = os.path.join(staging_dir, "temp_ayon_package.sbs")
    path = os.path.normpath(path)
    sd_pkg_mgr.savePackageAs(temp_package, fileAbsPath=path)

    return temp_package, path


def create_project_with_from_template(project_settings=None):
    """Create Project from template setting

    Args:
        project_settings (str, optional): project settings. Defaults to None.
    """
    sd_context = sd.getContext()
    sd_app = sd_context.getSDApplication()
    sd_pkg_mgr = sd_app.getPackageMgr()

    if project_settings is None:
        project_settings = get_current_project_settings()

    project_name = get_current_project_name()
    package, package_filepath = create_tmp_package_for_template(
        sd_pkg_mgr, project_name
    )

    resources_dir = sd_app.getPath(SDApplicationPath.DefaultResourcesDir)
    project_creation_settings = project_settings["substancedesigner"].get(
        "project_creation", {})

    project_template_settings = project_creation_settings.get(
        "project_templates", [])
    if not project_creation_settings:
        return

    parsed_graph_names = []
    output_res_by_graphs = {}
    for project_template_setting in project_template_settings:
        graph_name = project_template_setting["name"]
        if project_template_setting["template_type"] == (
            "default_substance_template"
            ):
                project_template = project_template_setting.get(
                    "default_substance_template")
                template_filepath = get_template_filename_from_project(
                    resources_dir, project_template
                )
        elif project_template_setting["template_type"] == (
            "custom_template"
            ):
                custom_template = project_template_setting["custom_template"]
                project_template = custom_template["custom_template_graph"]
                if not project_template:
                    log.warning("Project template not filled. "
                                "Skipping project creation.")
                    continue

                template_filepath = custom_template["custom_template_path"]
                if not template_filepath:
                    log.warning("Template path not filled. "
                                "Skipping project creation.")
                    continue
                if not os.path.exists(template_filepath):
                    log.warning("Template path does not exist yet. "
                                "Skipping project creation.")
                    continue
        else:
            task_type_template = project_template_setting["task_type_template"]
            folder_path = get_current_folder_path()
            task_name = get_current_task_name()
            folder_entity = ayon_api.get_folder_by_path(
                project_name,
                folder_path,
                fields={"id"})
            task_entity = ayon_api.get_task_by_name(
                    project_name, folder_entity["id"], task_name
                )
            task_type = task_entity["taskType"]
            if task_type not in task_type_template["task_types"]:
                log.warning("Incorrect task types for the project. "
                            "Skipping project creation.")
                continue

            workdir = os.getenv("AYON_WORKDIR")

            try:
                os.makedirs(workdir)
            except OSError as e:
                # An already existing working directory is fine.
                if e.errno == errno.EEXIST:
                    pass
                else:
                    raise

            template_filepath = os.path.join(workdir, f"{task_type}.sbs")

        template_filepath = os.path.normpath(template_filepath)
        if  project_template_setting["template_type"] == (
            "task_type_template"
            ):
            for task_name in task_type_template["task_names"]:
                graph_name = f"{graph_name}_{task_name}"
                parsed_graph = parse_graph_from_template(
                    graph_name, task_name, template_filepath
                )
                parsed_graph_names.append(parsed_graph)
                output_res_by_graphs[graph_name] = (
                    project_template_setting["default_texture_resolution"]
                )
        else:
            parsed_graph = parse_graph_from_template(
                graph_name, project_template, template_filepath)
            parsed_graph_names.append(parsed_graph)

            output_res_by_graphs[graph_name] = (
                project_template_setting["default_texture_resolution"]
            )

    # add graph with template
    add_graphs_to_package(parsed_graph_names, package_filepath)

    sd_pkg_mgr.unloadUserPackage(package)
    sd_pkg_mgr.loadUserPackage(
        package_filepath, updatePackages=True, reloadIfModified=True
    )

    # set user-defined resolution by graphs
    set_output_resolution_by_graphs(output_res_by_graphs)


def get_template_filename_from_project(resources_dir,
                                       project_template):
    """Get template filename from ayon project settings

    Args:
        resources_dir (sd.api.sdapplication.SDApplicationPath): resources dir
        project_template (str): project template name

    Returns:
        str: absolute filepath of the sbs template file.
    """
    templates_dir = os.path.join(resources_dir, "templates")
    if project_template == "empty":
        return os.path.join(templates_dir, "01_empty.sbs")
    if project_template in [
        "metallic_roughness",
        "metallic_roughness_anisotropy",
        "metallic_roughness_coated",
        "metallic_roughness_sheen",
        "adobe_standard_material"
    ]:
        return os.path.join(
            templates_dir, "02_pbr_metallic_roughness.sbs")
    elif project_template == "specular_glossiness":
        return os.path.join(
            templates_dir, "03_pbr_specular_glossiness.sbs")
    elif project_template == "blinn":
        return os.path.join(
            templates_dir, "04_blinn.sbs")
    elif project_template == "scan_metallic_roughness":
        return os.path.join(
            templates_dir, "05_scan_pbr_metallic_roughness.sbs")
    elif project_template == "scan_specular_glossiness":
        return os.path.join(
            templates_dir, "06_scan_pbr_specular_glossiness.sbs")
    elif project_template == "axf_to_metallic_roughness":
        return os.path.join(
            templates_dir, "07_axf_to_pbr_metallic_roughness.sbs")
    elif project_template == "axf_to_specular_glossiness":
        return os.path.join(
            templates_dir, "08_axf_to_pbr_specular_glossiness.sbs")
    elif project_template == "axf_to_axf":
        return os.path.join(
            templates_dir, "09_axf_to_axf.sbs")
    elif project_template == "studio_panorama":
        return os.path.join(
            templates_dir, "10_studio_panorama.sbs")
    elif project_template in [
        "sp_filter_generic",
        "sp_filter_specific",
        "sp_filter_channel_mesh_maps",
        "sp_generator_mesh_maps"
    ]:
        return os.path.join(
            templates_dir, "11_substance_painter.sbs")
    elif project_template == "sample_filter":
        return os.path.join(
            templates_dir, "12_substance_sampler.sbs")
    elif project_template == "clo_metallic_roughness":
        return os.path.join(
            templates_dir, "13_clo_metallic_roughness.sbs")

    return None


def set_output_resolution_by_graphs(resolution_size_by_graphs):
    """Set output resolution per graph accordingly to Ayon settings

    Args:
        package (sd.api.sdpackage.SDPackage): temp package for graphs
        resolution_size_by_graphs (dict): resolution data for each graph
    """
    for graph_name, res_size in resolution_size_by_graphs.items():
        graph = get_sd_graph_by_name(graph_name)
        output_size = graph.getPropertyFromId(
                "$outputsize", SDPropertyCategory.Input
        )
        graph.setPropertyInheritanceMethod(
            output_size, SDPropertyInheritanceMethod.Absolute
        )
        graph.setPropertyValue(
            output_size, SDValueInt2.sNew(int2(res_size, res_size))
        )
