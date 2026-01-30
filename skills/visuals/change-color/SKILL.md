---
name: change-color
description: Change colors in product images using Visuals AI. Use when user wants to modify clothing colors or visualize different color variations. Supports local images and Shopify product URLs.
allowed-tools: Bash, AskUserQuestion
disable-model-invocation: false
---

# Change Color Workflow

Change the color of clothing in product images using Visuals AI's color transformation workflow.

## Supported inputs

- **Local image files**: PNG, JPG, JPEG (will convert to base64)
- **Shopify product URLs**: `https://www.zenoficial.com.br/products/...` (will fetch available images)
- **Direct image URLs**: Any publicly accessible image URL

## Required environment variable

Ensure `VISUALS_API_KEY` is set in your environment. This is the master API key for Visuals AI.

## Workflow steps

### 1. Determine input type

Check if the user provided:
- A local file path (check if file exists)
- A Shopify product URL (contains `zenoficial.com.br/products/`)
- A direct image URL (starts with `http://` or `https://`)

### 2. Handle Shopify product URLs

If the input is a Shopify product URL, fetch available images first:

```bash
curl -X POST ${VISUALS_API_URL:-https://visuals-ai.vercel.app}/api/zen-product \
  -H "Content-Type: application/json" \
  -d '{"productUrl": "<shopify_url>", "action": "fetch"}'
```

This returns:
```json
{
  "productName": "Product Name",
  "productUrl": "...",
  "images": [
    {"id": "...", "thumbnailUrl": "...", "fullUrl": "..."},
    ...
  ]
}
```

**Present the images to the user** using AskUserQuestion with the thumbnail URLs so they can choose which image to use. Show the product name and let them select from the available images.

After the user selects an image, upload it to get a fal.ai URL:

```bash
curl -X POST ${VISUALS_API_URL:-https://visuals-ai.vercel.app}/api/zen-product \
  -H "Content-Type: application/json" \
  -d '{"imageUrl": "<selected_fullUrl>", "action": "upload"}'
```

This returns:
```json
{
  "url": "https://v3b.fal.media/files/...",
  "originalUrl": "..."
}
```

Use the `url` field as the image URL for the workflow.

### 3. Handle local files

If the input is a local file path, resize if needed to avoid 10MB payload limit:

```bash
file_path="<path>"

# Check file size and resize if necessary to avoid 10MB limit
# Base64 adds ~33% overhead, so target max 7MB original size
file_size=$(stat -f%z "$file_path" 2>/dev/null || stat -c%s "$file_path" 2>/dev/null)
max_size=$((7 * 1024 * 1024))  # 7MB

if [ "$file_size" -gt "$max_size" ]; then
  echo "Image is too large ($(($file_size / 1024 / 1024))MB), resizing to fit 10MB limit..."

  # Resize to max 1024px width using sips (macOS) or convert (ImageMagick)
  if command -v sips >/dev/null 2>&1; then
    sips --resampleWidth 1024 "$file_path" --out /tmp/resized-image.png >/dev/null 2>&1
    file_path="/tmp/resized-image.png"
  elif command -v convert >/dev/null 2>&1; then
    convert "$file_path" -resize 1024x "$file_path"
  else
    echo "Warning: Image may be too large. Install ImageMagick for auto-resize."
  fi
fi

# Detect mime type from extension
mime_type="image/jpeg"
if [[ "$file_path" == *.png ]]; then
  mime_type="image/png"
elif [[ "$file_path" == *.webp ]]; then
  mime_type="image/webp"
fi

# Convert to base64 data URL
base64_data=$(base64 -i "$file_path" | tr -d '\n')
image_url="data:${mime_type};base64,${base64_data}"
```

### 4. Parse color and prompt

Extract from user's request:
- **Target color**: Hex code (e.g., `#0000FF` for blue) or color name that you convert to hex
- **Prompt**: Description of what to change (e.g., "Change dress to blue")

Common color conversions:
- red → `#FF0000`
- blue → `#0000FF`
- green → `#00FF00`
- black → `#000000`
- white → `#FFFFFF`
- yellow → `#FFFF00`
- pink → `#FFC0CB`

### 5. Execute workflow

Use Node.js to construct JSON payload (avoids shell escaping issues with large base64 strings):

```bash
# Set API credentials
API_URL="${VISUALS_API_URL:-https://visuals-ai.vercel.app}"
API_KEY="${VISUALS_API_KEY}"

# Create JSON payload using Node.js (handles large base64 strings properly)
node -e "
const fs = require('fs');
const payload = {
  workflowId: 'change-color',
  inputs: {
    targetColor: '<hex_color>',
    prompt: '<description>'
  },
  images: {
    productImage: '${image_url}'
  }
};
fs.writeFileSync('/tmp/workflow_payload.json', JSON.stringify(payload));
"

# Execute workflow
response=$(curl -s -X POST "$API_URL/api/workflow/execute" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/workflow_payload.json)

echo "$response"
```

Response:
```json
{
  "success": true,
  "jobId": "uuid",
  "status": "pending"
}
```

### 6. Poll for completion

Extract job ID and poll until completed:

```bash
# Extract job ID from response
job_id=$(echo "$response" | grep -o '"jobId":"[^"]*"' | cut -d'"' -f4)

# Poll for completion (max 60 seconds)
API_URL="${VISUALS_API_URL:-https://visuals-ai.vercel.app}"
API_KEY="${VISUALS_API_KEY}"

for i in {1..20}; do
  sleep 3

  poll_response=$(curl -s "$API_URL/api/workflow/status/$job_id" \
    -H "Authorization: Bearer $API_KEY")

  job_status=$(echo "$poll_response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

  echo "Polling attempt $i: $job_status"

  if [ "$job_status" = "completed" ]; then
    output_url=$(echo "$poll_response" | grep -o '"outputUrl":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Success! Output: $output_url"
    break
  elif [ "$job_status" = "failed" ]; then
    error_msg=$(echo "$poll_response" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
    echo "❌ Failed: $error_msg"
    break
  fi
done
```

Response when completed:
```json
{
  "jobId": "uuid",
  "status": "completed",
  "workflowId": "change-color",
  "outputUrl": "https://v3b.fal.media/files/...",
  "outputType": "image",
  "processingDurationMs": 24123
}
```

### 7. Return result

When status is `"completed"`:
- Show the output image URL
- Optionally display the image inline if possible
- Mention the color transformation was successful

When status is `"failed"`:
- Show the error message from the response
- Suggest troubleshooting steps

## Example usage

**User request:**
"Change this dress to blue: https://www.zenoficial.com.br/products/vestido-midi-fluido"

**Your actions:**
1. Fetch product images from Shopify URL
2. Show user the 3 available images and ask which to use
3. User selects image #2
4. Upload selected image to get fal.ai URL
5. Execute workflow with target color `#0000FF` and prompt "Change dress to blue"
6. Poll for completion
7. Show final result URL

## Notes

- The `modelId` parameter is optional. If not specified, defaults to `fal-ai/nano-banana-pro/edit`
- Maximum image size: Files larger than 5MB may need resizing
- Processing time: Usually 15-30 seconds for image workflows
- Error handling: If you get "Unprocessable Entity", the image URL might be invalid. For Shopify URLs, make sure to use the uploaded fal.ai URL, not the direct Shopify CDN URL.
