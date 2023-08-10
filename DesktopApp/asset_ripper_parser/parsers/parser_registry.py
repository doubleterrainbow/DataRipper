from typing import List
from DesktopApp.asset_ripper_parser.parsers.parser_function import ParserFunction


class ParserRegistry:
    """
    Stores list of linkers and their readable names
    """

    registry = []

    @classmethod
    def include(cls, *args):
        """
        Usage:

        @ParserRegistry.include("Drop Tables", [FileTags.DropTables])
        def linkDropTables(props):
            pass
        """

        def decorator(fn):
            cls.registry.append(
                ParserFunction(label=args[0], tags=args[1], callable=fn)
            )
            return fn

        return decorator
