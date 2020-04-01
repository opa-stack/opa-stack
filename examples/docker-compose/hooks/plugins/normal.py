from opa.core.plugin import Hook


class fullname_hook(Hook):
    name = 'fullname'
    order = 1

    def run(self, firstname, lastname):
        return f'{firstname} {lastname}'
