from opa.core.plugin import BasePlugin


def say_hello():
    return "Hei"


class Plugin(BasePlugin):
    def startup(self, register_hook):
        register_hook('say_hello', say_hello)
