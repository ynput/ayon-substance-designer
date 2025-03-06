# -*- coding: utf-8 -*-
"""Creator plugin for creating textures."""
from ayon_core.pipeline import CreatedInstance, Creator, CreatorError

from ayon_substancedesigner.api.pipeline import (
    get_instances,
    set_instance,
    set_instances,
    remove_instance
)
from .lib import get_current_graph_name


SETTINGS_CATEGORY = "substancedesigner"


class TextureCreator(Creator):
    """Create a texture set."""
    settings_category = SETTINGS_CATEGORY

    def create(self, product_name, instance_data, pre_create_data):
        current_graph_name = get_current_graph_name()
        if not current_graph_name:
            raise CreatorError("Can't create a Texture Set instance without "
                               "the Substance Designer Graph.")

        instance_data["graph_name"] = current_graph_name

        instance = self.create_instance_in_context(product_name,
                                                   instance_data)
        set_instance(
            instance_id=instance["instance_id"],
            instance_data=instance.data_to_store()
        )

    def collect_instances(self):
        for instance in get_instances():
            if (instance.get("creator_identifier") == self.identifier or
                    instance.get("productType") == self.product_type):
                self.create_instance_in_context_from_existing(instance)

    def update_instances(self, update_list):
        instance_data_by_id = {}
        for instance, _changes in update_list:
            # Persist the data
            instance_id = instance.get("instance_id")
            instance_data = instance.data_to_store()
            instance_data_by_id[instance_id] = instance_data
        set_instances(instance_data_by_id, update=True)

    def remove_instances(self, instances):
        for instance in instances:
            remove_instance(instance["instance_id"])
            self._remove_instance_from_context(instance)

    # Helper methods (this might get moved into Creator class)
    def create_instance_in_context(self, product_name, data):
        instance = CreatedInstance(
            self.product_type, product_name, data, self
        )
        self.create_context.creator_adds_instance(instance)
        return instance

    def create_instance_in_context_from_existing(self, data):
        instance = CreatedInstance.from_existing(data, self)
        self.create_context.creator_adds_instance(instance)
        return instance
