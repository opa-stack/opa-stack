"""
Minimal demo that does nothing but exists and has a setup
"""

from opa.core.plugin import BasePlugin


class Plugin(BasePlugin):
    def startup(self, register_hook, register_driver):
        """
        Called when booting up the application (before 'app' is available).
        Use this if you want to register a hook or a driver
        """
        pass

    def setup(self, app):
        """
        app is available, which can add routes and so on..
        """
        pass
