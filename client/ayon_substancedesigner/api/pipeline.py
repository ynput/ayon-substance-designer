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
    register_loader_plugin_path,
    AVALON_CONTAINER_ID
)
from ayon_core.settings import get_current_project_settings
from ayon_core.pipeline.context_tools import version_up_current_workfile

from ayon_substancedesigner import SUBSTANCE_DESIGNER_HOST_DIR

from .lib import (
    package_manager,
    qt_ui_manager,
    get_package_from_current_graph,
    set_sd_metadata,
    parsing_sd_data
)
from .project_creation import create_project_with_from_template

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
        create_project_with_from_template()

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
            return []

        return parsing_sd_data(
            current_package, AYON_METADATA_CONTAINERS_KEY,
            is_dictionary=False
        )

    def update_context_data(self, data, changes):
        current_package = get_package_from_current_graph()
        if not current_package:
            return

        set_sd_metadata(AYON_METADATA_CONTEXT_KEY, data)

    def get_context_data(self):
        current_package = get_package_from_current_graph()
        if not current_package:
            return {}

        return parsing_sd_data(
            current_package, AYON_METADATA_CONTEXT_KEY) or {}


    def _install_menu(self):
        from ayon_core.tools.utils import host_tools
        qt_ui = qt_ui_manager()
        parent = qt_ui.getMainWindow()

        project_settings = get_current_project_settings()
        tab_menu_label = os.environ.get("AYON_MENU_LABEL") or "AYON"
        menu = qt_ui.newMenu(
            menuTitle=tab_menu_label, objectName=tab_menu_label
        )

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

        if project_settings["core"]["tools"]["ayon_menu"].get(
            "version_up_current_workfile"):
                action = menu.addAction("Version Up Workfile")
                action.triggered.connect(version_up_current_workfile)

        action = menu.addAction("Work Files...")
        action.triggered.connect(
            lambda: host_tools.show_workfiles(parent=parent)
        )
        self.menu = menu

    def _uninstall_menu(self):
        if self.menu:
            tab_menu_label = os.environ.get("AYON_MENU_LABEL") or "AYON"
            ctx = sd.getContext()
            sd_app = ctx.getSDApplication()
            ui_mgr = sd_app.getQtForPythonUIMgr()
            # Delete the menu
            if ui_mgr.findMenuFromObjectName() == tab_menu_label:
                ui_mgr.deleteMenu(objectName=tab_menu_label)

            self.menu.destroy()

        self.menu = None


def imprint(current_package, name, namespace, context,
            loader, identifier, options=None):
    """Imprint a loaded container with metadata.

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        name (str): Name of resulting assembly
        namespace (str): Namespace under which to host container
        context (dict): Asset information
        loader (load.LoaderPlugin): loader instance used to produce container.
        identifier(str): SDResource identifier
        options(dict): options

    Returns:
        None

    """
    data = {
        "schema": "ayon:container-2.0",
        "id": AVALON_CONTAINER_ID,
        "name": str(name),
        "namespace": str(namespace) if namespace else None,
        "loader": str(loader.__class__.__name__),
        "representation": context["representation"]["id"],
        "project_name": context["project"]["name"],
        "objectName": identifier
    }
    if options:
        for key, value in options.items():
            data[key] = value
    container_data = parsing_sd_data(
        current_package, AYON_METADATA_CONTAINERS_KEY, is_dictionary=False)
    container_data.append(data)
    set_sd_metadata(AYON_METADATA_CONTAINERS_KEY, container_data)


def remove_container_metadata(container):
    """Helper method to remove the data for a specific container"""
    current_package = get_package_from_current_graph()
    all_container_metadata = parsing_sd_data(
        current_package, AYON_METADATA_CONTAINERS_KEY, is_dictionary=False)
    metadata_remainder = [
        container_data for container_data in all_container_metadata
        if container_data["objectName"] != container["objectName"]
    ]
    set_sd_metadata(AYON_METADATA_CONTAINERS_KEY, metadata_remainder)


def set_instance(instance_id, instance_data, update=False):
    """Helper method to directly set the data for a specific container

    Args:
        instance_id (str): Unique identifier for the instance
        instance_data (dict): The instance data to store in the metaadata.
    """
    set_instances({instance_id: instance_data}, update=update)


def set_instances(instance_data_by_id, update=False):
    """Store data for multiple instances at the same time.

    Args:
        instance_data_by_id (dict): instance data queried by id
        update (bool, optional): whether the data needs update.
            Defaults to False.
    """
    current_package = get_package_from_current_graph()
    if current_package:
        instances = parsing_sd_data(
            current_package, AYON_METADATA_INSTANCES_KEY) or {}
        for instance_id, instance_data in instance_data_by_id.items():
            if update:
                existing_data = instances.get(instance_id, {})
                existing_data.update(instance_data)
            else:
                instances[instance_id] = instance_data

        set_sd_metadata(AYON_METADATA_INSTANCES_KEY, instances)


def remove_instance(instance_id):
    """Helper method to remove the data for a specific container"""
    current_package = get_package_from_current_graph()
    if current_package:
        instances = parsing_sd_data(
            current_package, AYON_METADATA_INSTANCES_KEY) or {}
        instances.pop(instance_id, None)
        set_sd_metadata(AYON_METADATA_INSTANCES_KEY, instances)


def get_instances():
    """Return all instances stored in the project instances as a list"""
    current_package = get_package_from_current_graph()
    if not current_package:
        return []

    get_instances_by_id = parsing_sd_data(
        current_package, AYON_METADATA_INSTANCES_KEY) or {}
    return list(get_instances_by_id.values())
