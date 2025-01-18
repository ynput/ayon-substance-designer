import pyblish.api

from ayon_core.pipeline import registered_host


class CollectCurrentFile(pyblish.api.ContextPlugin):
    """Inject the current working file into context"""

    order = pyblish.api.CollectorOrder - 0.49
    label = "Current Workfile"
    hosts = ["substancedesigner"]

    def process(self, context):
        host = registered_host()
        path = host.get_current_workfile()
        if not path:
            self.log.error("Scene is not saved.")

        context.data["currentFile"] = path
        self.log.debug(f"Current workfile: {path}")
