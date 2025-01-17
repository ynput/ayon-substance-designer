import sd
import json
import ast

import six

import contextlib
from sd.api.sdapiobject import APIException
from sd.api.sdvalueserializer import SDValueSerializer



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
        sd.api.qtforpythonuimgrwrapper.QtForPythonUIMgrWrapper: Qt Python UI Manager
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


def set_sd_metadata(metadata_type: str, metadata: dict):
    """Set AYON-related metadata in Substance Painter

    Args:
        metadata_type (str): AYON metadata key
        metadata (dict): AYON-related metadata
    """
    # Need to convert dict to string first
    metadata_to_str = f"{json.dumps(metadata)}"
    metadata_value = sd.api.sdvaluestring.SDValueString.sNew(metadata_to_str)
    target_package = get_package_from_current_graph()
    package_metadata_dict = target_package.getMetadataDict()
    package_metadata_dict.setPropertyValueFromId(metadata_type, metadata_value)


def parsing_sd_data_to_dict(target_package, metadata_type: str):
    """Parse and convert Subsatnce Designer SDValue data to dictionary

    Args:
        target_package (sd.api.sdpackage.SDPackage): target SD Package
        metadata_type (str): Ayon metadata type

    Returns:
        dict: metadata dict
    """
    metadata_dict = {}
    package_metadata_dict = target_package.getMetadataDict()
    try:
        metadata_sd_value = package_metadata_dict.getPropertyValueFromId(
            metadata_type)
        metadata_value = SDValueSerializer.sToString(metadata_sd_value)
        metadata_dict = ast.literal_eval(metadata_value, "{}")

    except APIException:
        pass

    return metadata_dict
