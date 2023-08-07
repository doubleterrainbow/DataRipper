from typing import List
from DesktopApp.linker_function import LinkerFunction

class LinkerRegistry:
    """
    Stores list of linkers and their readable names
    """
    linkers: List[LinkerFunction] = []
    
    @classmethod
    def register(cls, *args, **kwargs):
        """
        Usage: 
        
        @LinkerRegistry.register("Drop Tables", [FileTags.DropTables])
        def linkDropTables(props):
            pass
        """
        def decorator(fn):
            cls.linkers.append(
                LinkerFunction(
                    label=args[0], 
                    tags=args[1] if len(args) > 1 else None,
                    callable=fn 
                )
            )
            return fn
        return decorator
    
