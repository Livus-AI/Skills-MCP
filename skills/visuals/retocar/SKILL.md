---
name: retocar
description: Retouch and enhance product images. Use for removing wrinkles, improving lighting, or general image enhancement of product photos.
allowed-tools: Bash, AskUserQuestion
---

# Retocar (Retouch) Workflow

Enhance and retouch product images to improve quality, remove wrinkles, fix lighting, or make other improvements.

## Input handling

Follow the input handling pattern from `change-color` skill.

## Execute workflow

```bash
curl -X POST ${VISUALS_API_URL:-https://visuals-ai.vercel.app}/api/workflow/execute \
  -H "Authorization: Bearer ${VISUALS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "workflowId": "retocar",
    "inputs": {
      "prompt": "<retouching_instructions>"
    },
    "images": {
      "productImage": "<image_url_or_data_url>"
    }
  }'
```

Example prompts:
- "Remove wrinkles from the clothing"
- "Improve lighting and make colors more vibrant"
- "Clean up the background and enhance the product"
- "Fix shadows and make the image more professional"

Poll for completion as described in `change-color` skill.
