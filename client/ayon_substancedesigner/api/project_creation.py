# -*- coding: utf-8 -*-
import os
import sd
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
    Anatomy,
    tempdir,
    get_current_context
)
from ayon_core.pipeline.template_data import get_template_data
from ayon_core.lib import StringTemplate, filter_profiles
from ayon_core.settings import get_current_project_settings
from ayon_substancedesigner.api.lib import get_sd_graph_by_name


log = logging.getLogger("ayon_substancedesigner")


def parse_graph_from_template(graph_name, project_template, template_filepath):
    """Parse graph by project template name from Substance template file
    Args:
        graph_name (str): graph_name
        project_template (str): project template name
        template_filepath (str): Substance template filepath

    Returns:
        List[xml.etree.ElementTree.Element]: graph(s) from the select template

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

    if graph_element:
        identifier_element = graph_element.find('identifier')
        if identifier.attrib.get('v') == project_template:
            identifier_element.attrib['v'] = graph_name
    else:
        log.warning(
            f"Graph with identifier '{project_template}' "
            f"not found in {template_filepath}."
        )

    return graph_element


def parse_dependencies_from_template(template_filepath):
    """Parse dependencies from Substance template file

    Args:
        template_filepath (str): Substance template filepath

    Returns:
        List[xml.etree.ElementTree.Element]: dependencies from
            the select template
    """
    dependencies = []
    # Parse the template substance file
    substance_tree = etree.parse(template_filepath)
    substance_root = substance_tree.getroot()

    for element in substance_root.find('.//dependencies'):
        dependencies.append(element)
    return dependencies


def add_graphs_to_package(
        parsed_graph_names, parsed_dependencies, temp_package_filepath):
    """Add graphs to the temp package

    Args:
        parsed_graph_names (list): parsed graph names
        parsed_dependencies (list): parsed dependencies
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

    if parsed_dependencies:
        # Remove the existing <dependencies/> element if it exists
        dependencies_element = unsaved_root.find('dependencies')
        if dependencies_element is not None:
            # Find the <dependencies> element in Unsaved_Package.xml
            unsaved_root.remove(dependencies_element)

        new_dependencies_content = etree.Element('dependencies')
        # Append the copied <dependency> element
        new_dependencies_content.extend(parsed_dependencies)
        # Add the new <dependencies> to the root
        unsaved_root.append(new_dependencies_content)

    # Save the modified content for Substance file
    unsaved_tree.write(
        temp_package_filepath,
        encoding='utf-8',
        xml_declaration=True
    )

    log.info("All graphs are copied and pasted successfully!")


def create_tmp_package_for_template(sd_pkg_mgr, project_name):
    """Create temp substance package for template graph

    Args:
        sd_pkg_mgr (sd.api.sdpackagemgr.SDPackageMgr): package manager
        project_name (str): project_name

    Returns:
        sd.api.sdpackage.SDPackage, str: SD Package and template file path

    """
    temp_filename = "temp_ayon_package.sbs"
    for temp_package in sd_pkg_mgr.getUserPackages():
        path = temp_package.getFilePath()
        if os.path.basename(path) == temp_filename:
            return temp_package, path

    temp_package = sd_pkg_mgr.newUserPackage()
    staging_dir = tempdir.get_temp_dir(
        project_name, use_local_temp=True
    )
    path = os.path.join(staging_dir, temp_filename)
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

    context = get_current_context()
    project_name = context["project_name"]

    resources_dir = sd_app.getPath(SDApplicationPath.DefaultResourcesDir)
    project_creation_settings = project_settings["substancedesigner"].get(
        "project_creation", {})

    project_template_settings = project_creation_settings.get(
        "project_templates", [])
    if not project_creation_settings:
        return

    parsed_graph_names = []
    output_res_by_graphs = {}
    parsed_dependencies = []
    for project_template_setting in project_template_settings:
        graph_name = project_template_setting["grpah_name"]
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
                    log.warning("Project template not set. "
                                "Skipping project creation.")
                    continue

                path = custom_template["custom_template_path"]
                if not path:
                    log.warning("Template path not filled. "
                                "Skipping project creation.")
                    continue
                folder_entity, task_entity = _get_current_context_entities(
                    context)
                template_filepath = resolve_template_path(
                    path, project_name, folder_entity, task_entity
                )
                if not os.path.exists(template_filepath):
                    log.warning(
                        f"Template path '{template_filepath}' "
                        "does not exist yet.")
                    continue
        else:
            task_type_template = project_template_setting["task_type_template"]
            folder_entity, task_entity = _get_current_context_entities(context)
            filter_data = {
                "task_types": task_type_template["task_types"]
            }
            matched_task_type = filter_profiles(
                project_template_settings, filter_data, logger=log)
            if not matched_task_type:
                log.warning("No matching task_type found. "
                            "Skipping project creation.")
                continue

            path = task_type_template["path"]
            template_filepath = resolve_template_path(
                path, project_name, folder_entity, task_entity)
            if not os.path.exists(template_filepath):
                log.warning(f"Template filepath '{template_filepath}'"
                            " not found.")
                continue

            project_template = task_entity["name"]

        template_filepath = os.path.normpath(template_filepath)

        parsed_graph = parse_graph_from_template(
            graph_name, project_template, template_filepath)
        if parsed_graph is not None:
            parsed_graph_names.append(parsed_graph)

        output_res_by_graphs[graph_name] = (
            project_template_setting["default_texture_resolution"]
        )
        parsed_dependency_paths = parse_dependencies_from_template(
            template_filepath)
        parsed_dependencies.extend(parsed_dependency_paths)

    if not parsed_graph_names:
        return

    # add graph with template
    package, package_filepath = create_tmp_package_for_template(
        sd_pkg_mgr, project_name
    )

    add_graphs_to_package(
        parsed_graph_names, parsed_dependencies, package_filepath
    )

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


def resolve_template_path(path, project_name, folder_entity, task_entity):
    """resolve template path for Substance files

    Args:
        path (_type_): template path to resolve
        project_name (str): project name
        folder_entity (dict): folder entity data
        task_name (str): task name

    Returns:
        str: resolved path for Substance template file
    """
    anatomy = Anatomy(project_name)
    project_entity = ayon_api.get_project(project_name)
    fill_data = get_template_data(
        project_entity, folder_entity, task_entity)
    fill_data["root"] = anatomy.roots
    result = StringTemplate.format_template(path, fill_data)
    if result.solved:
        path = result.normalized()
    return path


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


def _get_current_context_entities(context):
    """Get entity data from DB

    Args:
        project_name (str): project name

    Returns:
        dict, dict: folder entity, task entity
    """
    project_name = context["project_name"]
    folder_path = context["folder_path"]
    task_name = context["task_name"]
    folder_entity = ayon_api.get_folder_by_path(
        project_name, folder_path)
    task_entity = ayon_api.get_task_by_name(
            project_name, folder_entity["id"], task_name
        )
    return folder_entity, task_entity
