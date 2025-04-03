

def initializeSDPlugin():
    """Initialize AYON Plugin as Substance Designer Plugin
    """
    from ayon_core.pipeline import install_host
    from ayon_substancedesigner.api import SubstanceDesignerHost
    install_host(SubstanceDesignerHost())


def uninitializeSDPlugin():
    """Uninitialize AYON Plugin as Substance Designer Plugin
    """
    from ayon_core.pipeline import uninstall_host
    uninstall_host()


if __name__ == "__main__":
    initializeSDPlugin()
