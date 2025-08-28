# Required: lower case addon name e.g. 'deadline', otherwise addon
#   will be invalid
name = "substancedesigner"

# Optional: Addon title shown in UI, 'name' is used by default e.g. 'Deadline'
title = "Substance Designer"

# Required: Valid semantic version (https://semver.org/)
version = "0.1.1+dev"

# Name of client code directory imported in AYON launcher
# - do not specify if there is no client code
client_dir = "ayon_substancedesigner"
project_can_override_addon_version = True
app_host_name = "substancedesigner"

# Version compatibility with AYON server
ayon_server_version = ">=1.1.2"
# Version compatibility with AYON launcher
# ayon_launcher_version = ">=1.0.2"

# Mapping of addon name to version requirements
# - addon with specified version range must exist to be able to use this addon
ayon_required_addons = {
    "core": ">=1.0.12",
}
# Mapping of addon name to version requirements
# - if addon is used in same bundle the version range must be valid
ayon_compatible_addons = {}
