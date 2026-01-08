#!/bin/bash
# Automated release script for Working Tracker Desktop

set -e

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./release.sh <version>"
    echo "Example: ./release.sh 2.1.0"
    exit 1
fi

echo "🚀 Starting release process for v$VERSION"

# 1. Update version in package.json
echo "📝 Updating version to $VERSION..."
npm version $VERSION --no-git-tag-version

# 2. Commit version bump
git add package.json package-lock.json
git commit -m "chore: bump version to $VERSION"

# 3. Create and push tag
echo "🏷️  Creating tag v$VERSION..."
git tag -a "v$VERSION" -m "Release v$VERSION"
git push origin main
git push origin "v$VERSION"

echo "✅ Release process started!"
echo "📦 GitHub Actions will now:"
echo "   1. Build for Windows, macOS, Linux"
echo "   2. Sign and notarize binaries"
echo "   3. Upload to downloads server"
echo "   4. Update release metadata"
echo ""
echo "🔍 Monitor progress at:"
echo "   https://github.com/your-org/working-tracker/actions"
