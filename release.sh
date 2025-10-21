#!/bin/bash
# Simple release script for LinqConnect

set -e

# Get current version from manifest
CURRENT_VERSION=$(grep '"version"' custom_components/linqconnect/manifest.json | sed 's/.*"version": "\(.*\)".*/\1/')

# Prompt for version if not provided
if [ -z "$1" ]; then
    echo "Current version: $CURRENT_VERSION"
    read -p "Enter new version number (e.g., 1.0.0): " VERSION
else
    VERSION=$1
fi

# Validate version
if [ -z "$VERSION" ]; then
    echo "Error: Version number is required"
    exit 1
fi

echo "🚀 Releasing v$VERSION"
echo ""

# Update manifest.json
echo "📝 Updating manifest.json..."
sed -i '' "s/\"version\": \".*\"/\"version\": \"$VERSION\"/" custom_components/linqconnect/manifest.json

# Commit changes
echo "💾 Committing changes..."
git add .
git commit -m "Release v$VERSION"

# Create tag
echo "🏷️  Creating tag..."
git tag -a "v$VERSION" -m "Release v$VERSION"

# Push
echo "⬆️  Pushing to GitHub..."
git push origin main
git push origin "v$VERSION"

echo ""
echo "✅ Tag v$VERSION created and pushed!"
echo ""
echo "📦 Next: Create GitHub Release"
echo "   1. Go to: https://github.com/coltoneshaw/homeassistant-linqconnect/releases/new?tag=v$VERSION"
echo "   2. Title: v$VERSION"
echo "   3. Copy content from CHANGELOG.md"
echo "   4. Click 'Publish release'"
echo ""
echo "   Or install gh CLI and run: gh release create v$VERSION --notes-file CHANGELOG.md"
