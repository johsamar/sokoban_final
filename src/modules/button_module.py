from mesa.visualization.modules import TextElement


class ButtonModule(TextElement):
    def __init__(self, options):
        self.options = options

    def render(self, model):
        options_html = "".join([f"<option value='{option}'>{option}</option>" for option in self.options])
        return f"<select>{options_html}</select>"