from ayon_substancedesigner.api.plugin import TextureCreator


class CreateSbsar(TextureCreator):
    """Create a texture set."""
    identifier = "io.ayon.creators.substancedesigner.sbsar"
    label = "Sbsar"
    product_base_type = "sbsar"
    product_type = product_base_type
    icon = "picture-o"

    default_variant = "Main"
