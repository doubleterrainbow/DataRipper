class ParserFunction:
    """Contains information about function that is used to parse asset files,
    as well as a callable instance of that function.
    """

    def __init__(self, label, tags, func_callable):
        self.label = label
        self.tags = tags
        self.func_callable = func_callable


class ParserRegistry:
    """
    Stores list of parsers and their readable names
    """

    registry = []

    @classmethod
    def include(cls, *args):
        """
        Usage:

        @ParserRegistry.include("Drop Tables", [FileTags.DropTables])
        def parse_drop_tables(props):
            pass
        """

        def decorator(func):
            cls.registry.append(
                ParserFunction(label=args[0], tags=args[1], func_callable=func)
            )
            return func

        return decorator
