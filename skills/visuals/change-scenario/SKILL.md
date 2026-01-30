---
name: change-scenario
description: Change the background/scenario of product images. Use when user wants to place the model and product in a different setting or environment.
allowed-tools: Bash, AskUserQuestion
---

# Change Scenario Workflow

Change the background or environment where the model appears, keeping the model and clothing intact.

## Input handling

Follow the input handling pattern from `change-color` skill:
- Shopify URLs → fetch, user selects, upload
- Local files → base64 conversion
- Direct URLs → use as-is

## Execute workflow

```bash
curl -X POST ${LIVUS_API_URL:-https://visuals-ai.vercel.app}/api/workflow/execute \
  -H "Authorization: Bearer ${LIVUS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "workflowId": "change-scenario",
    "inputs": {
      "prompt": "<scenario_description>"
    },
    "images": {
      "productImage": "<image_url_or_data_url>"
    }
  }'
```

Example prompts:
- "Place the model on a beach at sunset"
- "Move to a modern urban street"
- "Studio background with soft lighting"
- "Outdoor garden setting"

Poll for completion as described in `change-color` skill.
