from mesa.visualization.modules import TextElement

class FileSelectModule(TextElement):
    def __init__(self):
        self.file_path = None

    def render(self, model):
        return """
            <script>
                function loadFile() {{
                    var input = document.getElementById('fileInput');
                    var file = input.files[0];
                    if (file) {{
                        var reader = new FileReader();
                        reader.onload = function(e) {{
                            var filename = file.name;
                            model.set_filename(filename);
                            console.log("Archivo seleccionado: " + filename);
                        }};
                        reader.readAsText(file);
                    }}
                }}
            </script>
            Seleccione un archivo: <input type='file' id='fileInput' onchange='loadFile()'>
        """