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
