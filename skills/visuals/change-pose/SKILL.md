---
name: change-pose
description: Change the pose/position of models in product images. Use when user wants to modify how a model is positioned or posed while wearing clothes.
allowed-tools: Bash, AskUserQuestion
---

# Change Pose Workflow

Change the pose or position of models in product images using Visuals AI.

## Input handling

Follow the same input handling pattern as `change-color` skill:
- **Shopify URLs**: Fetch images, let user choose, upload to fal.ai
- **Local files**: Resize if >7MB, convert to base64 data URL
- **Direct URLs**: Use as-is

**Important:** For images >7MB, auto-resize to 1024px width before base64 encoding to avoid 10MB payload limit.

See `change-color` skill for complete examples of:
- Image resizing (using sips or ImageMagick)
- JSON payload construction (using Node.js)
- Polling loop with proper variable names

## Execute workflow

Available pose references:
- `standing` - Em Pé (standing straight)
- `hand_on_hip` - Mão no Quadril (hand on hip)
- `walking` - Caminhando (walking)
- `leaning` - Encostada (leaning)
- `arms_crossed` - Braços Cruzados (arms crossed)

Or use a custom description like "arms raised above head" or "sitting cross-legged".

Follow the execution pattern from `change-color` skill:

```bash
# Set API credentials
API_URL="${VISUALS_API_URL:-https://visuals-ai.vercel.app}"
API_KEY="${VISUALS_API_KEY}"

# Create JSON payload using Node.js
node -e "
const fs = require('fs');
const payload = {
  workflowId: 'change-pose',
  inputs: {
    prompt: '<pose_description>',
    poseReference: '<pose_id>'
  },
  images: {
    productImage: '${image_url}'
  }
};
fs.writeFileSync('/tmp/workflow_payload.json', JSON.stringify(payload));
"

# Execute and poll (see change-color skill for complete polling loop)
response=$(curl -s -X POST "$API_URL/api/workflow/execute" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/workflow_payload.json)
```

Poll for completion using the polling loop from `change-color` skill.
