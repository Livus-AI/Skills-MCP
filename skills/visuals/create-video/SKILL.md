---
name: create-video
description: Create animated videos from product images. Use when user wants to animate a product photo or create a video showing movement.
allowed-tools: Bash, AskUserQuestion
---

# Create Video Workflow

Generate animated videos from static product images, adding movement and life to photos.

## Input handling

Follow the input handling pattern from `change-color` skill.

Optionally, this workflow can take a second image as the last frame for more controlled animation.

## Execute workflow

```bash
curl -X POST ${LIVUS_API_URL:-https://visuals-ai.vercel.app}/api/workflow/execute \
  -H "Authorization: Bearer ${LIVUS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "workflowId": "create-video",
    "inputs": {
      "prompt": "<animation_description>",
      "duration": "<4|6|8>"
    },
    "images": {
      "productImage": "<image_url_or_data_url>",
      "lastFrame": "<optional_last_frame_url>"
    }
  }'
```

**Parameters:**
- `prompt`: Description of desired animation (e.g., "Model walking forward", "Fabric flowing in the wind")
- `duration`: Video length in seconds (`"4"`, `"6"`, or `"8"`)
- `lastFrame` (optional): If provided, video will animate from first image to this image

**Output:** Returns a video URL (MP4 format) instead of an image.

Poll for completion as described in `change-color` skill. Note that `outputType` will be `"video"` instead of `"image"`.

## Example

"Create a 6-second video of the model walking forward"

```json
{
  "workflowId": "create-video",
  "inputs": {
    "prompt": "Model walking forward",
    "duration": "6"
  },
  "images": {
    "productImage": "https://..."
  }
}
```
