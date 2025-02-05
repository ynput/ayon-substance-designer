# -*- coding: utf-8 -*-
import sd
import json
import contextlib

from sd.api.sdapiobject import APIException


def package_manager():
    """Get Package Manager of Substance Designer

    Returns:
        sd.api.sdpackagemgr.SDPackageMgr: Package Manager
    """
    app = sd.getContext().getSDApplication()
    pkg_mgr = app.getPackageMgr()
    return pkg_mgr


def qt_ui_manager():
    """Get Qt Python UI Manager of Substance Designer

    Returns:
        sd.api.qtforpythonuimgrwrapper.QtForPythonUIMgrWrapper: Qt Python
            UI Manager
    """
    ctx = sd.getContext()
    sd_app = ctx.getSDApplication()
    qt_ui_mgr = sd_app.getQtForPythonUIMgr()
    return qt_ui_mgr


def get_package_from_current_graph():
    """Get Package from the current graph.

    Returns:
        sd.api.sdpackage.SDPackage: A package with SDResource
    """
    qt_ui = qt_ui_manager()
    current_graph = qt_ui.getCurrentGraph()
    if not current_graph:
        return None
    return current_graph.getPackage()


def get_current_graph_name():
    """Get the name of the current SD graph

    Returns:
        str: current SD graph name
    """
    qt_ui = qt_ui_manager()
    current_graph = qt_ui.getCurrentGraph()
    if not current_graph:
        return None

    return current_graph.getIdentifier()


def get_sd_graphs_by_package():
    """Get Substance Designer Graphs by package

    Returns:
        list: name of Substance Designer Graphs
    """
    current_package = get_package_from_current_graph()
    return [
        resource.getIdentifier()
        for resource in
        current_package.getChildrenResources(True)
        if resource.getClassName() == "SDSBSCompGraph"
    ]


def get_sd_graph_by_name(graph_name):
    """Get SD graph base on its name

    Args:
        graph_name (str): SD graph name

    Returns:
        sd.api.sdgraph.SDGraph: SD Graph
    """
    pkg_mgr = package_manager()
    for package in pkg_mgr.getUserPackages():
        for resource in package.getChildrenResources(True):
            if (
                resource.getClassName() == "SDSBSCompGraph"
                and resource.getIdentifier() == graph_name
            ):
                return resource


def get_map_identifiers_by_graph(target_graph_name):
    """Get map identifiers of the target SD graph

    Args:
        target_graph_name (str): target SD graph name

    Returns:
        list: all map identifiers
    """
    all_map_identifiers = []
    target_graph = get_sd_graph_by_name(target_graph_name)
    if target_graph:
        for output_node in target_graph.getOutputNodes():
            for output in output_node.getProperties(
                sd.api.sdproperty.SDPropertyCategory.Output):
                    all_map_identifiers.append(output.getId())

    return all_map_identifiers


def set_sd_metadata(metadata_type: str, metadata):
    """Set AYON-related metadata in Substance Painter

    Args:
        metadata_type (str): AYON metadata key
        metadata (dict/list): AYON-related metadata
    """
    # Need to convert dict to string first
    target_package = get_package_from_current_graph()
    metadata_to_str = f"{json.dumps(metadata)}"
    metadata_value = sd.api.sdvaluestring.SDValueString.sNew(metadata_to_str)
    package_metadata_dict = target_package.getMetadataDict()
    package_metadata_dict.setPropertyValueFromId(metadata_type, metadata_value)


def parsing_sd_data(target_package, metadata_type: str, is_dictionary=True):
    """Parse and convert Subsatnce Designer SDValue data to dictionary

    Args:
        target_package (sd.api.sdpackage.SDPackage): target SD Package
        metadata_type (str): Ayon metadata type

    Returns:
        dict/list: metadata dict
    """
    metadata = {} if is_dictionary else []
    package_metadata_dict = target_package.getMetadataDict()
    with contextlib.suppress(APIException):
        metadata_value = package_metadata_dict.getPropertyValueFromId(
            metadata_type).get()
        metadata = json.loads(metadata_value)

    return metadata
