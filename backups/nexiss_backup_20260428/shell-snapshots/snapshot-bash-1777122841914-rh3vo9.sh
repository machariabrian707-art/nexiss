# Snapshot file
# Unset all aliases to avoid conflicts with functions
unalias -a 2>/dev/null || true
shopt -s expand_aliases
# Check for rg availability
if ! (unalias rg 2>/dev/null; command -v rg) >/dev/null 2>&1; then
  alias rg='rg'
fi
export PATH='/c/Users/pc/bin:/mingw64/bin:/usr/local/bin:/usr/bin:/bin:/mingw64/bin:/usr/bin:/c/Users/pc/bin:/c/Users/pc/AppData/Local/Programs/Microsoft VS Code/10c8e557c8/resources/app/node_modules/@vscode/ripgrep/bin:/c/Users/pc/AppData/Local/Programs/Microsoft VS Code:/c/WINDOWS/system32:/c/WINDOWS:/c/WINDOWS/System32/Wbem:/c/WINDOWS/System32/WindowsPowerShell/v1.0:/c/WINDOWS/System32/OpenSSH:/c/Program Files/Intel/WiFi/bin:/c/Program Files/Common Files/Intel/WirelessCommon:/c/Program Files/Docker/Docker/resources/bin:/c/Program Files/GitHub CLI:/c/Users/pc/AppData/Local/Microsoft/WindowsApps:/c/Users/pc/AppData/Local/Programs/Microsoft VS Code/bin:/c/Users/pc/AppData/Local/GitHubDesktop/bin:/c/Users/pc/AppData/Local/Programs/cursor/resources/app/bin:/c/Users/pc/.local/bin:/c/Users/pc/.local/bin:/c/Users/pc/.local/bin:/c/Users/pc/.local/bin:/usr/bin/vendor_perl:/usr/bin/core_perl'
