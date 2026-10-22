from typing import Dict, Any

class CapabilityRegistry:
    """
    Centralized capability discovery and registration mechanism for the OneApp framework.
    Allows modules to register capabilities (like PolicyProviders) dynamically at runtime.
    """
    _capabilities: Dict[str, Any] = {}
    _providers: Dict[str, str] = {}
    
    @classmethod
    def register_capability(cls, name: str, provider_instance: Any, provider_name: str):
        """
        Registers a capability provider and its resolved name (e.g., 'DATABASE' or 'DEFAULT').
        """
        cls._capabilities[name] = provider_instance
        cls._providers[name] = provider_name
        
    @classmethod
    def get_capability(cls, name: str) -> Any:
        """
        Retrieves a registered capability provider by name.
        """
        return cls._capabilities.get(name)
        
    @classmethod
    def get_provider_name(cls, name: str) -> str:
        """
        Retrieves the name of the active provider for a capability.
        """
        return cls._providers.get(name, "UNINITIALIZED")
        
    @classmethod
    def get_all_capabilities(cls) -> Dict[str, str]:
        """
        Returns a mapping of capability names to their provider names for reporting.
        """
        return cls._providers.copy()
