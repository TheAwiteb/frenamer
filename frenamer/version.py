__all__ = "version", "version_info"

version = "0.2.3"


def version_info() -> str:
    import platform
    import sys
    from pathlib import Path

    info = {
        "frenamer version": version,
        "install path": Path(__file__).resolve().parent,
        "python version": sys.version,
        "platform": platform.platform(),
    }
    return "\n".join(f"{key}:{val}" for key, val in info.items())
