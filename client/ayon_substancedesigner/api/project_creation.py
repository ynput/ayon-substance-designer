# -*- coding: utf-8 -*-
import os
import sd
import logging
import xml.etree.ElementTree as etree

from sd.api.sdapplication import SDApplicationPath

from ayon_core.pipeline import tempdir, get_current_project_name
from ayon_core.settings import get_current_project_settings


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
        if identifier is not None and identifier.attrib.get('v') == project_template:
            graph_element = graph
            break

    if graph_element is None:
        log.warning(
            f"Graph with identifier '{project_template}' not found in {template_filepath}."
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
    unsaved_tree.write(temp_package_filepath, encoding='utf-8', xml_declaration=True)

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
    for package in sd_pkg_mgr.getUserPackages():
        for resource in package.getChildrenResources(True):
            if resource.getClassName() == "SDSBSCompGraph":
                return

    if project_settings is None:
        project_settings = get_current_project_settings()

    project_name = get_current_project_name()
    package, package_filepath = create_tmp_package_for_template(
        sd_pkg_mgr, project_name
    )

    resources_dir = sd_app.getPath(SDApplicationPath.DefaultResourcesDir)
    project_creation_settings = project_settings["substancedesigner"].get(
        "DesignerProjectCreation", {})
    project_template_settings = project_creation_settings.get(
        "project_templates", [])
    if not project_creation_settings:
        return

    parsed_graph_names = []
    for project_template_setting in project_template_settings:
        graph_name = project_template_setting["name"]
        project_template = project_template_setting["project_workflow"]
        template_filepath = get_template_filename_from_project_settings(
            resources_dir, project_template
        )
        template_filepath = os.path.normpath(template_filepath)
        parsed_graph = parse_graph_from_template(
            graph_name, project_template, template_filepath)
        parsed_graph_names.append(parsed_graph)

    # add graph with template
    add_graphs_to_package(parsed_graph_names, package_filepath)

    sd_pkg_mgr.unloadUserPackage(package)
    sd_pkg_mgr.loadUserPackage(
        package_filepath, updatePackages=True, reloadIfModified=True
    )


def get_template_filename_from_project_settings(resources_dir, project_template):
    """Get template filename from ayon project settings

    Args:
        resources_dir (sd.api.sdapplication.SDApplicationPath): resources directory
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
