#!/bin/bash
# Canvas AI CLI Setup Script

CLI_PATH="/home/tordm/dev/CanvasAIDashboard/cli.py"
ALIAS_NAME="canvas"

echo "╔══ CANVAS AI CLI SETUP ══╗"
echo "║ Configuring CLI tool..."
echo "╚═════════════════════════╝"

# Check if the CLI file exists
if [ ! -f "$CLI_PATH" ]; then
    echo "╔══ ERROR ══╗"
    echo "║ CLI file not found at:"
    echo "║ $CLI_PATH"
    echo "╚═══════════╝"
    exit 1
fi

# Make sure it's executable
chmod +x "$CLI_PATH"

# Add alias to bash profile
ALIAS_LINE="alias $ALIAS_NAME='python $CLI_PATH'"

# Check if alias already exists
if grep -q "alias $ALIAS_NAME=" ~/.bashrc; then
    echo "╔══ NOTICE ══╗"
    echo "║ Alias '$ALIAS_NAME' already exists"
    echo "║ Updating existing alias..."
    echo "╚════════════╝"
    sed -i "/alias $ALIAS_NAME=/c\\$ALIAS_LINE" ~/.bashrc
else
    echo "╔══ INSTALLING ══╗"
    echo "║ Adding alias to ~/.bashrc..."
    echo "╚════════════════╝"
    echo "" >> ~/.bashrc
    echo "# Canvas AI CLI" >> ~/.bashrc
    echo "$ALIAS_LINE" >> ~/.bashrc
fi

# Check if alias exists in current session
if ! command -v $ALIAS_NAME &> /dev/null; then
    echo "╔══ RELOADING ══╗"
    echo "║ Updating shell configuration..."
    echo "╚═══════════════╝"
    source ~/.bashrc
fi

echo ""
echo "╔══ SETUP COMPLETE ══╗"
echo "║ Canvas AI CLI is ready!"
echo "╚════════════════════╝"
echo ""
echo "╔══ USAGE EXAMPLES ══╗"
echo "║ $ALIAS_NAME health"
echo "║ $ALIAS_NAME ask \"Hvilke kurs har jeg?\""
echo "║ $ALIAS_NAME context"
echo "║ $ALIAS_NAME refresh"
echo "║ $ALIAS_NAME debug"
echo "╚════════════════════╝"
echo ""
echo "╔══ NOTICE ══╗"
echo "║ You may need to restart your terminal"
echo "║ or run 'source ~/.bashrc' for the"
echo "║ '$ALIAS_NAME' command to be available."
echo "╚════════════╝"
