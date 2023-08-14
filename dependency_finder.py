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
from parse_code import *

def find_import_structure(pyfile):
    # Uncover nesting of local imports
    import_structure = {pyfile:"TODO"}
    ls = [os.path.normpath(pyfile)]
    while len(ls):
        for l in ls:
            if l.endswith(".ipynb"):
                deps = CodeWithDependencies(code_str=JupyterNotebook(l).extract_code(),in_folder=os.path.dirname(pyfile))
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

def all_imports_of_type(import_type,import_structure,imports_set=set()):
    for imports in import_structure.values():
        imports_set = imports_set | set(imports[import_type])
    return sorted(list(imports_set))

def all_local_imports(import_structure):
    return all_imports_of_type("local",import_structure,set(import_structure.keys()))

def all_external_imports(import_structure):
    return all_imports_of_type("external",import_structure)

def all_shell_dependencies(import_structure):
    return all_imports_of_type("shell",import_structure)

def find_all_dependencies(pyfile,local_basedir=None):
    import_structure = find_import_structure(pyfile)

    local_imports = all_local_imports(import_structure)
    if local_basedir:
        local_imports = [p.replace(os.path.join(local_basedir,""),"") for p in local_imports]

    return {"local":local_imports,
            "external":all_external_imports(import_structure),
            "shell":all_shell_dependencies(import_structure)}

if __name__ == "__main__":
    import sys
    print(find_all_dependencies(sys.argv[0],local_basedir=os.getcwd()))
