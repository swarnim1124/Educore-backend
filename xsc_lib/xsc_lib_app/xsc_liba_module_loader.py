"""
File: xsc_liba_module_loader.py
Description: Dynamic module loader with in-memory caching for the OneApp Framework.

Author: Siddharth Amdal
App: OneApp

"""

import importlib
from typing import Any, Dict
from xsc_lib.xsc_lib_common.xsc_libc_exceptions import ModuleNotFoundException


class ModuleLoader:
    """
    Reusable framework service for dynamic module discovery and action instantiation.
    Implements an internal cache to avoid repeated reflection.
    """

    _cache: Dict[str, Any] = {
        "modules": {},
        "submodules": {},
        "actions": {},
        "mod_dirs": {},
    }

    @classmethod
    def _resolve_mod_dir(cls, module_name: str) -> str:
        """
        Resolves the actual on-disk module directory name in modules/ (case-insensitively).
        E.g. 'm_aaa' or 'm_AAA' resolves to 'm_AAA'.
        """
        if not module_name:
            return ""
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        snake_mod = XSCUtility.to_snake_case(module_name)
        mod_dir = snake_mod if snake_mod.startswith("m_") else f"m_{snake_mod}"
        if "mod_dirs" not in cls._cache:
            cls._cache["mod_dirs"] = {}
        if mod_dir in cls._cache["mod_dirs"]:
            return cls._cache["mod_dirs"][mod_dir]

        import os

        base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "modules")
        actual_dir = mod_dir
        if os.path.exists(base_dir):
            for folder in os.listdir(base_dir):
                if folder.lower() == mod_dir.lower():
                    actual_dir = folder
                    break

        cls._cache["mod_dirs"][mod_dir] = actual_dir
        return actual_dir

    @classmethod
    def load_action(
        cls, module_name: str, submodule_name: str, action_name: str
    ) -> Any:
        """
        Dynamically locate and return the Action function reference.
        Uses in-memory cache if available.
        """
        cache_key = f"{module_name}.{submodule_name}.{action_name}"

        # Check cache for Action function
        if cache_key in cls._cache["actions"]:
            return cls._cache["actions"][cache_key]

        # Resolve Submodule
        submodule = cls._load_submodule(module_name, submodule_name)

        # Locate wrapper class inside submodule (try exact, snake_case, sm_snake_case, PascalCase)
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        snake_sub = XSCUtility.to_snake_case(submodule_name)
        sm_snake_sub = snake_sub if snake_sub.startswith("sm_") else f"sm_{snake_sub}"
        pascal_sub = XSCUtility.to_pascal_case(submodule_name.replace("sm_", ""))

        wrapper_class = getattr(submodule, submodule_name, None)
        if not wrapper_class:
            wrapper_class = getattr(submodule, sm_snake_sub, None)
        if not wrapper_class:
            wrapper_class = getattr(submodule, snake_sub, None)
        if not wrapper_class:
            wrapper_class = getattr(submodule, pascal_sub, None)
        if not wrapper_class:
            wrapper_class = getattr(
                submodule, XSCUtility.to_pascal_case(submodule_name), None
            )
        if not wrapper_class:
            # Fallback to action name if class matches action
            wrapper_class = getattr(submodule, action_name, None)

        if not wrapper_class:
            raise ModuleNotFoundException(
                target=f"Submodule wrapper class '{sm_snake_sub}' not found in {module_name}.{submodule_name}"
            )

        # Locate Action function inside wrapper class
        action_func = getattr(wrapper_class, action_name, None)
        if not action_func:
            snake_action = XSCUtility.to_snake_case(action_name)
            action_func = getattr(wrapper_class, snake_action, None)
        if not action_func:
            action_func = getattr(wrapper_class, snake_sub, None)
        if not action_func:
            action_func = getattr(wrapper_class, sm_snake_sub, None)
        if not action_func:
            clean_sub = snake_sub.replace("sm_", "")
            action_func = getattr(wrapper_class, clean_sub, None)
        if not action_func:
            action_func = getattr(wrapper_class, "execute", None)

        if not action_func:
            raise ModuleNotFoundException(
                target=f"Action '{action_name}' in {module_name}.{submodule_name}"
            )

        # If wrapper_class is an uninstantiated class and action_func expects self, instantiate wrapper_class
        import inspect

        if inspect.isclass(wrapper_class):
            try:
                sig = inspect.signature(action_func)
                params = list(sig.parameters.keys())
                if params and params[0] in ("self", "sel", "cls"):
                    instance = wrapper_class()
                    func_name = getattr(action_func, "__name__", action_name)
                    bound_func = getattr(instance, func_name, None)
                    if not bound_func:
                        bound_func = getattr(instance, action_name, None)
                    if not bound_func:
                        snake_action = XSCUtility.to_snake_case(action_name)
                        bound_func = getattr(instance, snake_action, None)
                    if not bound_func:
                        bound_func = getattr(instance, "execute", None)
                    if bound_func:
                        action_func = bound_func
            except Exception:
                pass

        # Cache Action function
        cls._cache["actions"][cache_key] = action_func

        return action_func

    @classmethod
    def _load_submodule(cls, module_name: str, submodule_name: str) -> Any:
        """
        Dynamically load a submodule file using importlib.
        Resolves submodules directly from their Python modules with snake_case normalization.
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        cache_key = f"{module_name}.{submodule_name}"

        if cache_key in cls._cache["submodules"]:
            return cls._cache["submodules"][cache_key]

        mod_dir = module_name if module_name.startswith("m_") else f"m_{module_name}"
        actual_mod_dir = cls._resolve_mod_dir(module_name)
        snake_sub = XSCUtility.to_snake_case(submodule_name)
        sm_snake_sub = snake_sub if snake_sub.startswith("sm_") else f"sm_{snake_sub}"

        # Potential import target file names and package paths
        candidates = [
            (actual_mod_dir, f"{actual_mod_dir}_{sm_snake_sub}"),
            (actual_mod_dir, f"{actual_mod_dir}_{submodule_name}"),
            (actual_mod_dir, f"{actual_mod_dir}_{snake_sub}"),
            (mod_dir, f"{mod_dir}_{sm_snake_sub}"),
            (mod_dir, f"{mod_dir}_{submodule_name}"),
        ]

        cls._check_manifest(module_name, submodule_name)

        submodule = None

        for target_pkg, target_file in candidates:
            import_path = f"modules.{target_pkg}.{target_file}"
            try:
                submodule = importlib.import_module(import_path)
                break
            except ModuleNotFoundError as e:
                continue

        if submodule:
            cls._cache["submodules"][cache_key] = submodule
            return submodule

        raise ModuleNotFoundException(
            target=f"modules.{actual_mod_dir}.{actual_mod_dir}_{sm_snake_sub}"
        )

    @classmethod
    def _check_manifest(cls, module_name: str, submodule_name: str) -> None:
        """
        Attempt to load the module manifest.py to verify submodule support.
        """
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        actual_mod_dir = cls._resolve_mod_dir(module_name)
        manifest_cache_key = f"{actual_mod_dir}.manifest"

        if manifest_cache_key not in cls._cache["modules"]:
            try:
                manifest = importlib.import_module(f"modules.{actual_mod_dir}.manifest")
                cls._cache["modules"][manifest_cache_key] = manifest
            except ModuleNotFoundError:
                cls._cache["modules"][manifest_cache_key] = None

        manifest = cls._cache["modules"][manifest_cache_key]
        if manifest and hasattr(manifest, "SUPPORTED_SUBMODULES"):
            supported = set(manifest.SUPPORTED_SUBMODULES)
            snake_sub = XSCUtility.to_snake_case(submodule_name)
            sm_snake_sub = (
                snake_sub if snake_sub.startswith("sm_") else f"sm_{snake_sub}"
            )
            short_sub = (
                sm_snake_sub[3:] if sm_snake_sub.startswith("sm_") else sm_snake_sub
            )

            is_valid = any(
                item in supported
                for item in (
                    submodule_name,
                    snake_sub,
                    sm_snake_sub,
                    short_sub,
                    f"sm_{submodule_name}",
                )
            )
            if not is_valid:
                # Reload manifest from disk in case it was updated during runtime
                try:
                    manifest = importlib.reload(manifest)
                    cls._cache["modules"][manifest_cache_key] = manifest
                    if hasattr(manifest, "SUPPORTED_SUBMODULES"):
                        supported = set(manifest.SUPPORTED_SUBMODULES)
                        is_valid = any(
                            item in supported
                            for item in (
                                submodule_name,
                                snake_sub,
                                sm_snake_sub,
                                short_sub,
                                f"sm_{submodule_name}",
                            )
                        )
                except Exception:
                    pass

            if not is_valid:
                raise ModuleNotFoundException(
                    target=f"Submodule '{submodule_name}' not defined in manifest for {module_name}"
                )

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear the internal cache (useful for testing or hot-reloading).
        """
        cls._cache = {"modules": {}, "submodules": {}, "actions": {}}
