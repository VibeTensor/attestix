# Attestix Quick Start Demo (VHS tape file)
#
# Render with:
#   vhs public/demo.tape
#
# Installs: https://github.com/charmbracelet/vhs
#   - macOS:  brew install vhs
#   - Linux:  go install github.com/charmbracelet/vhs@latest
#   - Windows (WSL or Scoop):  scoop install vhs
#
# Output will be written to public/demo.gif (referenced by hero section).
# After regenerating, commit the GIF so it ships with the static export.

Output public/demo.gif

Set FontSize 18
Set Width 1200
Set Height 720
Set Padding 24
Set Theme "Dracula"
Set TypingSpeed 45ms
Set PlaybackSpeed 1.0

# Fake a fresh shell prompt
Type "# Install Attestix from PyPI"
Enter
Sleep 400ms

Type "pip install attestix"
Enter
Sleep 1500ms

Type "clear"
Enter
Sleep 300ms

Type "# Initialize a compliance workspace"
Enter
Sleep 400ms

Type "attestix init"
Enter
Sleep 1500ms

Type "# Check workspace status"
Enter
Sleep 400ms

Type "attestix status"
Enter
Sleep 1500ms

Type "# Verify a credential"
Enter
Sleep 400ms

Type "attestix verify ./credentials/agent-card.vc.json"
Enter
Sleep 2000ms

Type "# Every action is cryptographically signed and auditable."
Enter
Sleep 2000ms
