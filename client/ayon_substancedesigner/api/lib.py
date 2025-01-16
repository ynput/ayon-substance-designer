import sd


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
