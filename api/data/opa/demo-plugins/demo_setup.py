from opa import Setup


class Noop(Setup):
    def __init__(self, app):
        # The main app is available here. Setup is also run after everything else is setup.
        pass
