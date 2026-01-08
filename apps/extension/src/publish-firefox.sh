#!/bin/bash
# Publish to Firefox Add-ons

set -e

echo "🦊 Publishing to Firefox Add-ons..."

# Build extension
npm run build

# Create ZIP
cd dist
zip -r extension.zip *
cd ..

# Upload to Firefox Add-ons
curl "https://addons.mozilla.org/api/v5/addons/upload/" \
  -g -XPOST \
  --form "upload=@dist/extension.zip" \
  -H "Authorization: JWT $FIREFOX_JWT_TOKEN"

echo "✅ Extension uploaded to Firefox Add-ons"
