---
name: swap-face
description: Swap the model's face in a product image with a different person's face. Use when user wants to show the same clothing on a different model.
allowed-tools: Bash, AskUserQuestion
---

# Swap Face Workflow

Replace the model's face in a product image with a different person's face, keeping the clothing and pose intact.

## Input handling

This workflow requires TWO images:
1. **Product image** (with model wearing clothes) - handle as per `change-color` skill
2. **Face source** (the face to swap in) - can also be Shopify URL, local file, or direct URL

## Execute workflow

```bash
curl -X POST ${LIVUS_API_URL:-https://visuals-ai.vercel.app}/api/workflow/execute \
  -H "Authorization: Bearer ${LIVUS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "workflowId": "swap-face",
    "inputs": {
      "prompt": "Swap the face while keeping clothing and pose exactly the same"
    },
    "images": {
      "productImage": "<product_image_url>",
      "faceSource": "<face_source_url>"
    }
  }'
```

**Note**: Both images need proper handling:
- If either is a Shopify URL, fetch and let user choose the image
- If either is a local file, convert to base64
- If direct URLs, use as-is

Poll for completion as described in `change-color` skill.
