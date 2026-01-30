# Skills Best Practices

## Image Handling

All skills should follow these practices to avoid common issues:

### 1. Auto-resize large images

Images >7MB will exceed the 10MB payload limit after base64 encoding. Always check and resize:

```bash
file_size=$(stat -f%z "$file_path" 2>/dev/null || stat -c%s "$file_path" 2>/dev/null)
max_size=$((7 * 1024 * 1024))  # 7MB

if [ "$file_size" -gt "$max_size" ]; then
  # Resize to 1024px width using sips (macOS) or convert (ImageMagick)
  if command -v sips >/dev/null 2>&1; then
    sips --resampleWidth 1024 "$file_path" --out /tmp/resized-image.png >/dev/null 2>&1
    file_path="/tmp/resized-image.png"
  elif command -v convert >/dev/null 2>&1; then
    convert "$file_path" -resize 1024x "/tmp/resized-image.png"
    file_path="/tmp/resized-image.png"
  fi
fi
```

### 2. Use Node.js for JSON construction

Large base64 strings cause "argument list too long" errors with shell. Use Node.js:

```bash
API_URL="${VISUALS_API_URL:-https://visuals-ai.vercel.app}"
API_KEY="${VISUALS_API_KEY}"

node -e "
const fs = require('fs');
const payload = {
  workflowId: 'workflow-name',
  inputs: { /* ... */ },
  images: { productImage: '${image_url}' }
};
fs.writeFileSync('/tmp/workflow_payload.json', JSON.stringify(payload));
"

response=$(curl -s -X POST "$API_URL/api/workflow/execute" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/workflow_payload.json)
```

### 3. Proper polling loop

Avoid using `status` as a variable name (it's read-only in some shells). Use `job_status`:

```bash
job_id=$(echo "$response" | grep -o '"jobId":"[^"]*"' | cut -d'"' -f4)

for i in {1..20}; do
  sleep 3
  poll_response=$(curl -s "$API_URL/api/workflow/status/$job_id" \
    -H "Authorization: Bearer $API_KEY")

  job_status=$(echo "$poll_response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

  if [ "$job_status" = "completed" ]; then
    output_url=$(echo "$poll_response" | grep -o '"outputUrl":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Success! Output: $output_url"
    break
  elif [ "$job_status" = "failed" ]; then
    echo "❌ Failed"
    break
  fi
done
```

### 4. Environment variable expansion

Always assign to local variables first for reliable expansion:

```bash
# Good
API_URL="${VISUALS_API_URL:-https://visuals-ai.vercel.app}"
API_KEY="${VISUALS_API_KEY}"

curl ... -H "Authorization: Bearer $API_KEY"

# Avoid
curl ... -H "Authorization: Bearer ${VISUALS_API_KEY}"  # May not expand properly
```

## Reference Implementation

See `change-color/SKILL.md` for complete working examples of all these patterns.
