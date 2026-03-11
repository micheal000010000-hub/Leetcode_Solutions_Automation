"""Compatibility shim for CLI entrypoint.

Legacy implementations are archived under archive/legacy_versions/.
"""

from current.autosync import main


if __name__ == "__main__":
    main()
