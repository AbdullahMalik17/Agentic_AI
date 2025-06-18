# UV 
UV package manager that helps us to install data very fastly due to write in rust . All the other package manager give their own commands . But UV give command to like with other i.e uv pip . 

# Package Manager in Python
Package managers are tools that help you install, update, and manage Python packages and their dependencies . 

## Features 
- Faster than pip
- Virtual environment like anaconda
- TOML Configuration Support
- Lock file support 
- Require file support

## Common Commands
- `uv --version` - Check UV version
- `uv --help` - Get help information
- `uv pip list` - List installed packages
- `uv pip show [package]` - Show package details
- `uv pip freeze` - List all dependencies
- `uv init --package name` - to make package 
- `uv init folder ` - to make the uv folder 
- `uv run file or sripts in toml ` - we write file name when it is uv for folder except package 
- `uv pip install` - to install all depencies in TOML . 
- `uv add depencies` to add more installations
- `uv publish` to public our project .

# Make command project.script section 
- command name = "folder.file or folder "