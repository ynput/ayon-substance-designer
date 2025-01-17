# -*- coding: utf-8 -*-
"""Pipeline tools for Ayon Substance Designer integration."""
import os
import logging

# Substance 3D Designer modules
import sd

import pyblish.api

from ayon_core.host import HostBase, IWorkfileHost, ILoadHost, IPublishHost

from ayon_core.pipeline import (
    register_creator_plugin_path,
    register_loader_plugin_path
)

from ayon_substancedesigner import SUBSTANCE_DESIGNER_HOST_DIR

from .lib import (
    package_manager,
    qt_ui_manager,
    get_package_from_current_graph,
    set_sd_metadata,
    parsing_sd_data_to_dict
)


log = logging.getLogger("ayon_substancedesigner")

PLUGINS_DIR = os.path.join(SUBSTANCE_DESIGNER_HOST_DIR, "plugins")
PUBLISH_PATH = os.path.join(PLUGINS_DIR, "publish")
LOAD_PATH = os.path.join(PLUGINS_DIR, "load")
CREATE_PATH = os.path.join(PLUGINS_DIR, "create")
INVENTORY_PATH = os.path.join(PLUGINS_DIR, "inventory")

AYON_METADATA_CONTAINERS_KEY = "ayon_containers"  # child key
AYON_METADATA_CONTEXT_KEY = "ayon_context"        # child key
AYON_METADATA_INSTANCES_KEY = "ayon_instances"    # child key


class SubstanceDesignerHost(HostBase, IWorkfileHost, ILoadHost, IPublishHost):
    name = "substancedesigner"

    def __init__(self):
        super(SubstanceDesignerHost, self).__init__()
        self._has_been_setup = False
        self.menu = None
        self.callbacks = []
        self.shelves = []

    def install(self):
        pyblish.api.register_host("substancedesigner")

        pyblish.api.register_plugin_path(PUBLISH_PATH)
        register_loader_plugin_path(LOAD_PATH)
        register_creator_plugin_path(CREATE_PATH)

        # log.info("Installing callbacks ... ")
        # self._register_callbacks()

        log.info("Installing menu ... ")
        self._install_menu()

        self._has_been_setup = True

    def uninstall(self):
        self._uninstall_menu()
        # self._deregister_callbacks()

    def workfile_has_unsaved_changes(self):
        package = get_package_from_current_graph()
        if not package:
            return False
        return package.isModified()

    def get_workfile_extensions(self):
        # support .sbsar and .sbsasm for read-only
        return [".sbs", ".sbsar", ".sbsasm"]

    def save_workfile(self, dst_path=None):
        pkg_mgr = package_manager()
        package = get_package_from_current_graph()
        if package:
            pkg_mgr.savePackageAs(package, fileAbsPath=dst_path)
            return dst_path

    def open_workfile(self, filepath):
        pkg_mgr = package_manager()
        pkg_mgr.loadUserPackage(
            filepath, updatePackages=False, reloadIfModified=False
        )
        return filepath

    def get_current_workfile(self):
        package = get_package_from_current_graph()
        if package:
            return package.getFilePath()

        return None

    def get_containers(self):
        current_package = get_package_from_current_graph()
        if not current_package:
            return

        containers = parsing_sd_data_to_dict(
            current_package, AYON_METADATA_CONTAINERS_KEY)
        if containers:
            for key, container in containers.items():
                container["objectName"] = key
                yield container

    def update_context_data(self, data, changes):
        current_package = get_package_from_current_graph()
        if not current_package:
            return

        set_sd_metadata(current_package, AYON_METADATA_CONTEXT_KEY)

    def get_context_data(self):
        current_package = get_package_from_current_graph()
        if not current_package:
            return

        return parsing_sd_data_to_dict(current_package, AYON_METADATA_CONTEXT_KEY) or {}


    def _install_menu(self):
        from ayon_core.tools.utils import host_tools
        qt_ui = qt_ui_manager()
        parent = qt_ui.getMainWindow()

        tab_menu_label = os.environ.get("AYON_MENU_LABEL") or "AYON"
        menu = qt_ui.newMenu(menuTitle=tab_menu_label, objectName=tab_menu_label)

        action = menu.addAction("Create...")
        action.triggered.connect(
            lambda: host_tools.show_publisher(parent=parent,
                                              tab="create")
        )

        action = menu.addAction("Load...")
        action.triggered.connect(
            lambda: host_tools.show_loader(parent=parent, use_context=True)
        )

        action = menu.addAction("Publish...")
        action.triggered.connect(
            lambda: host_tools.show_publisher(parent=parent,
                                              tab="publish")
        )

        action = menu.addAction("Manage...")
        action.triggered.connect(
            lambda: host_tools.show_scene_inventory(parent=parent)
        )

        action = menu.addAction("Library...")
        action.triggered.connect(
            lambda: host_tools.show_library_loader(parent=parent)
        )

        menu.addSeparator()
        action = menu.addAction("Work Files...")
        action.triggered.connect(
            lambda: host_tools.show_workfiles(parent=parent)
        )
        self.menu = menu

    def _uninstall_menu(self):
        if self.menu:
            # self.menu.destroy()
            tab_menu_label = os.environ.get("AYON_MENU_LABEL") or "AYON"
            ctx = sd.getContext()
            sd_app = ctx.getSDApplication()
            ui_mgr = sd_app.getQtForPythonUIMgr()
            # Delete the menu
            if ui_mgr.findMenuFromObjectName() == tab_menu_label:
                ui_mgr.deleteMenu(objectName=tab_menu_label)

        self.menu = None
