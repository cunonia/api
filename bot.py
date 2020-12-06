import importlib
import json
from pathlib import Path

from discord.ext.commands import Bot
from discord.ext.commands.bot import _default
from pluginbase import PluginBase

from api.cog import BotCog


class PluginBot(Bot):
    def __init__(self, command_prefix, help_command=_default, description=None, **options):
        super().__init__(command_prefix, help_command, description, **options)

        self.plugins = {}
        self.cog_instances = {}
        plugin_source = PluginBase(package="plugins").make_plugin_source(searchpath=["./plugins"])
        for i in plugin_source.list_plugins():
            self.load_plugin(i)

        if Path("settings.json").exists():
            self._settings: dict = json.load(Path("settings.json").open())
        else:
            self._settings: dict = {}

    def load_plugin(self, plugin_name: str):
        mod = importlib.import_module("." + plugin_name, package="plugins")
        self.plugins[plugin_name] = mod
        self.cog_instances[plugin_name] = []
        for i in self.plugins[plugin_name].__cogs__:
            cog_instance = i(self)
            self.add_cog(cog_instance)
            self.cog_instances[plugin_name].append(cog_instance)

    def unload_plugin(self, plugin_name: str):
        for i in self.cog_instances[plugin_name]:
            self.remove_cog(i.qualified_name)
        self.plugins.pop(plugin_name)
        self.cog_instances.pop(plugin_name)

    def reload_plugin(self, plugin_name: str):
        for i in self.cog_instances[plugin_name]:
            self.remove_cog(i.qualified_name)
        self.plugins[plugin_name] = importlib.reload(self.plugins[plugin_name])
        self.cog_instances[plugin_name] = []
        for i in self.plugins[plugin_name].__cogs__:
            cog_instance = i(self)
            self.add_cog(cog_instance)
            self.cog_instances[plugin_name].append(cog_instance)

    def reload_cog(self, cog_name: str):
        mod_name = None
        for i in self.cog_instances:
            if cog_name in [cog.qualified_name for cog in self.cog_instances[i]]:
                mod_name = i
                break
        if mod_name:
            self.reload_plugin(mod_name)

    async def close(self):
        json.dump(self._settings, Path("settings.json").open("w"), indent=4)
        await super().close()

    def settings(self, cog_name=None):
        if not cog_name:
            return self._settings
        if isinstance(cog_name, BotCog):
            cog_name = type(cog_name).__name__
        if not self._settings.get(cog_name):
            self._settings[cog_name] = {}
        return self._settings[cog_name]
