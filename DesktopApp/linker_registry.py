from typing import List
from DesktopApp.linker_function import LinkerFunction

class LinkerRegistry:
    """
    Stores list of linkers and their readable names
    """
    linkers: List[LinkerFunction] = []
    
    @classmethod
    def register(cls, *args):
        """
        Usage: 
        
        @LinkerRegistry.register("Drop Tables", "drop table")
        def linkDropTables(props):
            pass
        
        """
        def decorator(fn):
            cls.linkers.append(
                LinkerFunction(
                    label=args[0], 
                    tag=args[1] if len(args) > 1 else None,
                    callable=fn 
                )
            )
            return fn
        return decorator
    
