import importlib
import json
import sys
from pathlib import Path
from typing import cast

from discord.ext.commands import Bot, Cog
from pluginbase import PluginBase


class PluginBot(Bot):
    def __init__(self, command_prefix, custom_load_order=None, **options):
        super().__init__(command_prefix, **options)

        self.plugins = {}
        self.cog_instances = {}
        if Path(sys.argv[1]).exists():
            self._settings: dict = json.load(Path(sys.argv[1]).open(encoding="utf-8"))
        else:
            self._settings: dict = {}

        self.custom_load_order = custom_load_order
        self.plugin_source = PluginBase(package="plugins").make_plugin_source(searchpath=["./plugins"])

        self.return_code = 0

    async def setup_hook(self) -> None:
        for i in self.custom_load_order or cast(list, self.plugin_source.list_plugins()):
            await self.load_plugin(i)
        return await super().setup_hook()

    async def load_plugin(self, plugin_name: str):
        mod = importlib.import_module("." + plugin_name, package="plugins")
        self.plugins[plugin_name] = mod
        self.cog_instances[plugin_name] = []
        for i in self.plugins[plugin_name].__cogs__:
            cog_instance = i(self)
            await self.add_cog(cog_instance)
            self.cog_instances[plugin_name].append(cog_instance)

    async def unload_plugin(self, plugin_name: str):
        for i in self.cog_instances[plugin_name]:
            await self.remove_cog(i.qualified_name)
        self.plugins.pop(plugin_name)
        self.cog_instances.pop(plugin_name)

    async def reload_plugin(self, plugin_name: str):
        for i in self.cog_instances[plugin_name]:
            await self.remove_cog(i.qualified_name)
        self.plugins[plugin_name] = importlib.reload(self.plugins[plugin_name])
        self.cog_instances[plugin_name] = []
        for i in self.plugins[plugin_name].__cogs__:
            cog_instance = i(self)
            await self.add_cog(cog_instance)
            self.cog_instances[plugin_name].append(cog_instance)

    async def reload_cog(self, cog_name: str):
        mod_name = None
        for i in self.cog_instances:
            if cog_name in [cog.qualified_name for cog in self.cog_instances[i]]:
                mod_name = i
                break
        if mod_name:
            await self.reload_plugin(mod_name)
        else:
            raise ModuleNotFoundError

    async def close(self):
        json.dump(self._settings, Path(sys.argv[1]).open("w", newline="\n"), indent=4)
        await super().close()

    def settings(self, cog_name=None):
        if not cog_name:
            return self._settings
        if isinstance(cog_name, Cog):
            cog_name = type(cog_name).__name__
        if not self._settings.get(cog_name):
            self._settings[cog_name] = {}
        return self._settings[cog_name]
