# -*- coding: utf-8 -*-
import os
import sd
from sd.api.sdapplication import SDApplicationPath
from sd.api.sbs.sdsbscompgraph import SDSBSCompGraph
from ayon_core.pipeline import tempdir, get_current_project_name
from ayon_core.settings import get_current_project_settings



# def metallic_roughness_template(graph_name):
#     xml_data = f"""
# <graph><identifier v="{"{graph_name}"}"/><uid v="1530982368"/>
# <graphtype v="material"/><graphOutputs><graphoutput><identifier v="basecolor"/>
# <uid v="1213284336"/><attributes><label v="Base Color"/></attributes>
# <usages><usage><components v="RGBA"/><name v="baseColor"/></usage></usages>
# <group v="Material"/></graphoutput><graphoutput><identifier v="normal"/>
# <uid v="1213284338"/><attributes><label v="Normal"/></attributes>
# <usages><usage><components v="RGBA"/><name v="normal"/></usage></usages>
# <group v="Material"/></graphoutput><graphoutput><identifier v="roughness"/>
# <uid v="1213284340"/><attributes><label v="Roughness"/></attributes><usages>
# <usage><components v="RGBA"/><name v="roughness"/></usage></usages>
# <channels v="2"/><group v="Material"/></graphoutput><graphoutput>
# <identifier v="metallic"/><uid v="1213284342"/><attributes><label v="Metallic"/>
# </attributes><usages><usage><components v="RGBA"/><name v="metallic"/></usage>
# </usages><channels v="2"/><group v="Material"/></graphoutput><graphoutput>
# <identifier v="height"/><uid v="1279137031"/><attributes><label v="Height"/>
# </attributes><usages><usage><components v="RGBA"/><name v="height"/></usage>
# </usages><channels v="2"/><group v="Material"/></graphoutput><graphoutput>
# <identifier v="ambientocclusion"/><uid v="1359211721"/><attributes>
# <label v="Ambient Occlusion"/></attributes><usages><usage>
# <components v="RGBA"/><name v="ambientOcclusion"/></usage></usages><channels v="2"/>
# <group v="Material"/></graphoutput></graphOutputs><compNodes><compNode>
# <uid v="1213284337"/><connections><connection><identifier v="inputNodeOutput"/>
# <connRef v="1359211355"/><connRefOutput v="1359211356"/></connection>
# </connections><GUILayout><gpos v="-48 -240 0"/></GUILayout><compImplementation>
# <compOutputBridge><output v="1213284336"/></compOutputBridge></compImplementation>
# </compNode><compNode><uid v="1213284339"/><connections><connection>
# <identifier v="inputNodeOutput"/><connRef v="1359211383"/><connRefOutput v="1359211384"/>
# </connection></connections><GUILayout><gpos v="-48 -80 0"/></GUILayout><compImplementation>
# <compOutputBridge><output v="1213284338"/></compOutputBridge></compImplementation></compNode>
# <compNode><uid v="1213284341"/><connections><connection><identifier v="inputNodeOutput"/>
# <connRef v="1359211391"/><connRefOutput v="1359211392"/></connection></connections><GUILayout>
# <gpos v="-48 80 0"/></GUILayout><compImplementation><compOutputBridge><output v="1213284340"/>
# </compOutputBridge></compImplementation></compNode><compNode><uid v="1213284343"/><connections><connection>
# <identifier v="inputNodeOutput"/><connRef v="1359211407"/><connRefOutput v="1359211408"/>
# </connection></connections><GUILayout><gpos v="-48 240 0"/></GUILayout><compImplementation>
# <compOutputBridge><output v="1213284342"/></compOutputBridge></compImplementation></compNode><compNode>
# <uid v="1279137030"/><connections><connection><identifier v="inputNodeOutput"/><connRef v="1359211415"/>
# <connRefOutput v="1359211408"/></connection></connections><GUILayout><gpos v="-48 560 0"/></GUILayout>
# <compImplementation><compOutputBridge><output v="1279137031"/></compOutputBridge></compImplementation>
# </compNode><compNode><uid v="1359211355"/><GUILayout><gpos v="-208 -240 0"/></GUILayout><compOutputs>
# <compOutput><uid v="1359211356"/><comptype v="1"/></compOutput></compOutputs><compImplementation>
# <compFilter><filter v="uniform"/><parameters><parameter><name v="outputcolor"/><relativeTo v="0"/>
# <paramValue><constantValueFloat4 v="0.5 0.5 0.5 1"/></paramValue></parameter></parameters></compFilter>
# </compImplementation></compNode><compNode><uid v="1359211383"/><GUILayout><gpos v="-208 -80 0"/>
# </GUILayout><compOutputs><compOutput><uid v="1359211384"/><comptype v="1"/></compOutput>
# </compOutputs><compImplementation><compFilter><filter v="normal"/><parameters><parameter>
# <name v="input2alpha"/><relativeTo v="0"/><paramValue><constantValueBool v="0"/></paramValue>
# </parameter></parameters></compFilter></compImplementation></compNode><compNode><uid v="1359211391"/>
# <GUILayout><gpos v="-208 80 0"/></GUILayout><compOutputs><compOutput><uid v="1359211392"/><comptype v="2"/>
# </compOutput></compOutputs><compImplementation><compFilter><filter v="uniform"/><parameters><parameter>
# <name v="colorswitch"/><relativeTo v="0"/><paramValue><constantValueBool v="0"/></paramValue></parameter>
# <parameter><name v="outputcolor"/><relativeTo v="0"/><paramValue><constantValueFloat4 v="0.25 0.25 0.25 1"/>
# </paramValue></parameter></parameters></compFilter></compImplementation></compNode>
# <compNode><uid v="1359211407"/><GUILayout><gpos v="-208 240 0"/></GUILayout><compOutputs><compOutput>
# <uid v="1359211408"/><comptype v="2"/></compOutput></compOutputs><compImplementation><compFilter>
# <filter v="uniform"/><parameters><parameter><name v="colorswitch"/><relativeTo v="0"/><paramValue>
# <constantValueBool v="0"/></paramValue></parameter></parameters></compFilter></compImplementation></compNode>
# <compNode><uid v="1359211415"/><GUILayout><gpos v="-208 560 501"/></GUILayout><compOutputs><compOutput><uid v="1359211408"/>
# <comptype v="2"/></compOutput></compOutputs><compImplementation><compFilter><filter v="uniform"/><parameters><parameter>
# <name v="colorswitch"/><relativeTo v="0"/><paramValue><constantValueBool v="0"/></paramValue></parameter><parameter>
# <name v="outputcolor"/><relativeTo v="0"/><paramValue><constantValueFloat4 v="0.5 0.5 0.5 1"/></paramValue></parameter>
# </parameters></compFilter></compImplementation></compNode><compNode><uid v="1359211719"/><GUILayout><gpos v="-208 400 0"/>
# </GUILayout><compOutputs><compOutput><uid v="1359211408"/><comptype v="2"/></compOutput></compOutputs><compImplementation>
# <compFilter><filter v="uniform"/><parameters><parameter><name v="colorswitch"/><relativeTo v="0"/><paramValue><constantValueBool v="0"/>
# </paramValue></parameter><parameter><name v="outputcolor"/><relativeTo v="0"/><paramValue><constantValueFloat4 v="1 1 1 1"/></paramValue>
# </parameter></parameters></compFilter></compImplementation></compNode><compNode><uid v="1359211720"/><connections><connection>
# <identifier v="inputNodeOutput"/><connRef v="1359211719"/><connRefOutput v="1359211408"/></connection></connections>
# <GUILayout><gpos v="-48 400 0"/></GUILayout><compImplementation><compOutputBridge><output v="1359211721"/></compOutputBridge>
# </compImplementation></compNode></compNodes><baseParameters/><options><option><name v="defaultParentSize"/><value v="11x11"/>
# </option></options><root><rootOutputs><rootOutput><output v="1213284336"/><format v="0"/><usertag v=""/>
# </rootOutput><rootOutput><output v="1213284338"/><format v="0"/><usertag v=""/></rootOutput><rootOutput>
# <output v="1213284340"/><format v="0"/><usertag v=""/></rootOutput><rootOutput><output v="1213284342"/><format v="0"/>
# <usertag v=""/></rootOutput><rootOutput><output v="1279137031"/><format v="0"/><usertag v=""/></rootOutput><rootOutput>
# <output v="1359211721"/><format v="0"/><usertag v=""/></rootOutput></rootOutputs></root></graph>

# """.format(graph_name)

#     return xml_data


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
    sd_pkg_mgr.savePackageAs(temp_package, fileAbsPath=path)

    return temp_package, path


def add_graph_from_template(project_settings=None):
    if project_settings is None:
        project_settings = get_current_project_settings()
    project_name = get_current_project_name()
    sd_context = sd.getContext()
    sd_app = sd_context.getSDApplication()
    sd_pkg_mgr = sd_app.getPackageMgr()
    package, filepath = create_tmp_package_for_template(
        sd_pkg_mgr, project_name
    )
    resources_dir = sd_app.getPath(SDApplicationPath.DefaultResourcesDir)
    project_creation_settings = project_settings["substancedesigner"].get(
        "DesignerProjectCreation", {})
    project_template_settings = project_creation_settings.get(
        "project_templates", [])
    for project_template_setting in project_template_settings:
        graph_name = project_template_setting["name"]
        project_template = project_template_setting["project_workflow"]
        template_filename = get_template_filename_from_project_settings(
            resources_dir, project_template)
        if not template_filename:
            new_empty_graph = SDSBSCompGraph.sNew(package)
            new_empty_graph.setIdentifier(graph_name)
            return
    #TODO: template setup with xml edit

    sd_pkg_mgr.loadUserPackage(
        filepath, updatePackages=True, reloadIfModified=True
    )


def get_template_filename_from_project_settings(resources_dir, project_template):
    """Get template filename from ayon project settings

    Args:
        resources_dir (sd.api.sdapplication.SDApplicationPath): resources directory
        project_template (str): project template name

    Returns:
        str: absolute filepath of the sbs template file.
    """
    if project_template in [
        "metallic_roughness",
        "metallic_roughness_anisotropy",
        "metallic_roughness_coated",
        "metallic_roughness_sheen",
        "adobe_standard_material"
    ]:
        return os.path.join(
            resources_dir, "02_pbr_metallic_roughness.sbs")
    elif project_template == "specular_glossiness":
        return os.path.join(
            resources_dir, "03_pbr_specular_glossiness.sbs")
    elif project_template == "blinn":
        return os.path.join(
            resources_dir, "04_blinn.sbs")
    elif project_template == "scan_metallic_roughness":
        return os.path.join(
            resources_dir, "05_scan_pbr_metallic_roughness.sbs")
    elif project_template == "scan_specular_glossiness":
        return os.path.join(
            resources_dir, "06_scan_pbr_specular_glossiness.sbs")
    elif project_template == "axf_to_metallic_roughness":
        return os.path.join(
            resources_dir, "07_axf_to_pbr_metallic_roughness.sbs")
    elif project_template == "axf_to_specular_glossiness":
        return os.path.join(
            resources_dir, "08_axf_to_pbr_specular_glossiness.sbs")
    elif project_template == "axf_to_axf":
        return os.path.join(
            resources_dir, "09_axf_to_axf.sbs")
    elif project_template == "studio_panorama":
        return os.path.join(
            resources_dir, "10_studio_panorama.sbs")
    elif project_template in [
        "sp_filter_generic",
        "sp_filter_specific",
        "sp_filter_channel_mesh_maps",
        "sp_generator_mesh_maps"
    ]:
        return os.path.join(
            resources_dir, "11_substance_painter.sbs")
    elif project_template == "sample_filter":
        return os.path.join(
            resources_dir, "12_substance_sampler.sbs")
    elif project_template == "clo_metallic_roughness":
        return os.path.join(
            resources_dir, "13_clo_metallic_roughness.sbs")

    return None
