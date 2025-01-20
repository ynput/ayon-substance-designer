# -*- coding: utf-8 -*-
"""Creator plugin for creating workfiles."""

import ayon_api

from ayon_core.pipeline import CreatedInstance, AutoCreator

from ayon_substancedesigner.api.pipeline import (
    set_instances,
    set_instance,
    get_instances
)

import sd


class CreateWorkfile(AutoCreator):
    """Workfile auto-creator."""
    identifier = "io.ayon.creators.substancedesigner.workfile"
    label = "Workfile"
    product_type = "workfile"
    icon = "document"

    default_variant = "Main"
    settings_category = "substancedesigner"

    def create(self):
        pass

    def collect_instances(self):
        pass

    def update_instances(self, update_list):
        pass

    def create_instance_in_context(self, product_name, data):
        return None

    def create_instance_in_context_from_existing(self, data):
        return None
