---
name: remove-model
description: Remove the model from product images, leaving only the clothing on a clean background. Use for creating flat lay or ghost mannequin product shots.
allowed-tools: Bash, AskUserQuestion
---

# Remove Model Workflow

Remove the model from product images, leaving only the clothing item on a white or transparent background.

## Input handling

Follow the input handling pattern from `change-color` skill.

## Execute workflow

```bash
curl -X POST ${VISUALS_API_URL:-https://visuals-ai.vercel.app}/api/workflow/execute \
  -H "Authorization: Bearer ${VISUALS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "workflowId": "remove-model",
    "inputs": {
      "prompt": "Remove the model, keep only the clothing",
      "backgroundType": "<white|transparent>"
    },
    "images": {
      "productImage": "<image_url_or_data_url>"
    }
  }'
```

**backgroundType** options:
- `white` - Place clothing on pure white background (default, better for e-commerce)
- `transparent` - Transparent background (PNG with alpha channel)

Poll for completion as described in `change-color` skill.
