#!/bin/bash
# Publish to Chrome Web Store

set -e

echo "🔵 Publishing to Chrome Web Store..."

# Build extension
npm run build

# Create ZIP
cd dist
zip -r extension.zip *
cd ..

# Upload to Chrome Web Store
curl -X PUT \
  -H "Authorization: Bearer $CHROME_ACCESS_TOKEN" \
  -H "x-goog-api-version: 2" \
  -T dist/extension.zip \
  "https://www.googleapis.com/upload/chromewebstore/v1.1/items/$CHROME_EXTENSION_ID"

echo "✅ Extension uploaded to Chrome Web Store"
