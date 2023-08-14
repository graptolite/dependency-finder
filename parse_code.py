# Copyright (C) 2023  Yingbo Li
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re
import json
import os

class JupyterNotebook():
    def __init__(self,notebook_file):
        self.notebook_file = notebook_file
        with open(notebook_file) as infile:
            self.notebook = json.load(infile)

    def __repr__(self):
        return f"Jupyter Notebook file: {self.notebook_file}"

    def extract(self,cell_type):
        # Isolate and extract one type of description cell type from notebook.
        def _handle_source(source):
            if isinstance(source,list):
                return "\n".join(source)
            else:
                return source
        content = "\n".join([_handle_source(cell["source"]) for cell in self.notebook["cells"] if cell["cell_type"]==cell_type])
        return content

    def extract_code(self):
        # Isolate and extract code cells from notebook. Content is effectively one long script that should do the same think as running the notebook.
        code = self.extract("code")
        return code

class CodeWithDependencies():
    def __init__(self,code_str=None,in_folder=os.getcwd(),pyfile=None):
        if code_str:
            self.code = code_str
            self.basedir = os.path.abspath(in_folder)
        elif pyfile:
            with open(pyfile) as infile:
                self.code = infile.read()
            self.basedir = os.path.dirname(os.path.abspath(pyfile))
        else:
            raise TypeError("No code or code file provided")

        self.densified_code = re.sub("\s","",self.code)

        self.paths = self.find_paths(self.basedir)
        self.all_imports = self.find_all_imports()
        self.shell_dependencies = self.find_shell_dependencies()
        self.local_importable_paths = self.find_local_importable_paths(self.paths)
        self.local_importables = self.local_importable_paths.keys()

        # Remove local imports to isolate external imports (though this includes system/base Python packages as well).
        self.external_imports = set(self.all_imports) - set(self.local_importables)
        # Names of local imports.
        local_imports = set(self.all_imports).intersection(self.local_importables)
        # Paths to local imports.
        self.local_imports = [self.local_importable_paths[x] for x in local_imports]

    def __repr__(self):
        return f"Code with\t{len(self.external_imports)} external imports\n\t\t{len(self.local_imports)} local imports\n\t\t{len(self.shell_dependencies)} shell dependencies"

    def find_paths(self,basedir):
        paths = [basedir] + \
            [os.path.join(basedir,p) for p in re.findall('sys\.path\.insert\(.*?,"(.*?)"\)',self.densified_code)]
        paths = [p for p in paths if os.path.exists(p)]
        return paths

    def find_all_imports(self):
        code = self.code
        all_imports = re.findall("^[\s]*from ([\S]*) import",code,flags=re.MULTILINE)
        for match_str in all_imports:
            code = code.replace(f"from {match_str} import","")
        all_imports.extend(re.findall("^[\s]*import ([\S]*)",code,flags=re.MULTILINE))
        return all_imports

    def find_local_importable_paths(self,paths):
        # Find all python files in all paths available to the notebook.
        local_importables = dict()
        for p in paths:
            pyfiles = [f for f in os.listdir(p) if f.endswith(".py")]
            for pyfile in pyfiles:
                local_importables[pyfile.replace(".py","")] = os.path.join(p,pyfile)
        return local_importables

    def find_shell_dependencies(self):
        densified_code = re.sub("\s","",self.code)
        shell_dependencies = re.findall('subprocess\.(call|Popen)\(\["(.*?)"',densified_code)
        shell_dependencies = [m_str[1] for m_str in shell_dependencies]
        return set(shell_dependencies)

def find_import_structure(pyfile):
    # Uncover nesting of local imports
    import_structure = {pyfile:"TODO"}
    ls = [os.path.normpath(pyfile)]
    while len(ls):
        for l in ls:
            if pyfile.endswith(".ipynb"):
                deps = CodeWithDependencies(code_str=JupyterNotebook(pyfile).extract_code(),in_folder=os.path.dirname(pyfile))
            else:
                # Assume base Python
                deps = CodeWithDependencies(pyfile=l)
            sub_local_imports = list(map(os.path.normpath,deps.local_imports))
            import_structure[l] = {"local":sub_local_imports,
                                   "external":deps.external_imports,
                                   "shell":deps.shell_dependencies}
            considered_local_imports = import_structure.keys()
            for sub_local_import in sub_local_imports:
                if sub_local_import not in considered_local_imports:
                    import_structure[sub_local_import] = "TODO"
        ls = [l for l,imports in import_structure.items() if imports=="TODO"]
    return import_structure
