# Usage
In all parts of the file, finding:
- "local" dependencies - imports from Python files in the same folder (or a folder accessible by the Python file via sys.path).
- "external" dependencies - imports from installed packages/modules.
- "shell" dependencies - shell commands called by subprocess.Popen or subprocess.call (extracted as first command in list of commands provided to those functions).

Where the command importing a "local" or "external" dependency (i.e.    `from ... import` or `import ...`) starts the line (though whitespace may be in front).

## Import
> `from dependency_finder import find_all_dependencies`
<br/> `find_all_dependencies(<python file>, <shared dir>)`

Where `<python file>` is the file (`.py` or `.ipynb` file) to search for dependencies in, and `<shared dir>` is a directory that should be removed from the local import file paths before returning the data.
## Commandline
> $ `python dependency_finder.py <python file>`

Where `<python file>` is the file (`.py` or `.ipynb` file) to search for dependencies in. Removes the current directory from local import file paths (i.e. equivalent to running `find_all_dependencies(<python file>, os.getcwd())`) - though this behaviour can be changed in source if undesired.

Example: 

> $ `python dependency_finder.py dependency_finder.py`

Returns:

> `{'local': ['parse_code.py', 'dependency_finder.py'], 'external': ['json', 'os', 're', 'sys'], 'shell': []}`

# GNU GPL License Notice
Copyright (C) 2022  Yingbo Li

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
