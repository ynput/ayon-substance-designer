from ayon_substancedesigner.api.plugin import TextureCreator


class CreateSbsar(TextureCreator):
    """Create a texture set."""
    identifier = "io.ayon.creators.substancedesigner.sbsar"
    label = "Sbsar"
    product_type = "sbsar"
    icon = "picture-o"

    default_variant = "Main"
    settings_category = "substancedesigner"
