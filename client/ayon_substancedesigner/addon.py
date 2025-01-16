import os
from ayon_core.addon import AYONAddon, IHostAddon

from .version import __version__

SUBSTANCE_DESIGNER_HOST_DIR = os.path.dirname(os.path.abspath(__file__))


class SubstanceDesignerAddon(AYONAddon, IHostAddon):
    name = "substancedesigner"
    version = __version__
    host_name = "substancedesigner"

    def add_implementation_envs(self, env, _app):
        # Add requirements to SUBSTANCE_PAINTER_PLUGINS_PATH
        plugin_path = os.path.join(SUBSTANCE_DESIGNER_HOST_DIR, "deploy")
        plugin_path = plugin_path.replace("\\", "/")
        if env.get("SBS_DESIGNER_PYTHON_PATH"):
            plugin_path += os.pathsep + env["SBS_DESIGNER_PYTHON_PATH"]

        env["SBS_DESIGNER_PYTHON_PATH"] = plugin_path

        # Log in Substance Painter doesn't support custom terminal colors
        env["AYON_LOG_NO_COLORS"] = "1"

    def get_launch_hook_paths(self, app):
        if app.host_name != self.host_name:
            return []
        return [
            os.path.join(SUBSTANCE_DESIGNER_HOST_DIR, "hooks")
        ]

    def get_workfile_extensions(self):
        return [".sbs", ".sbsar", ".sbsasm"]
