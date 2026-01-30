# Visuals AI Visual Workflows

AI skills for transforming product images using Visuals AI's visual workflows.

## Overview

These skills enable AI agents to interact with Visuals AI's image transformation workflows. They support local images, direct URLs, and Shopify product URLs with intelligent image handling including auto-resize and proper authentication.

## Available Skills

### 🎨 change-color
Transform clothing colors in product images. Supports hex color codes or color names.

**Use when**: User wants to modify clothing colors or visualize different color variations.

### 🕺 change-pose
Modify the pose or position of models in product images.

**Use when**: User wants to change how a model is positioned while wearing clothes.

### 🌅 change-scenario
Replace backgrounds and settings in product images.

**Use when**: User wants to change the scene, environment, or background.

### 👔 remove-model
Extract clothing from images, removing the model completely.

**Use when**: User wants to see the garment without the model (ghost mannequin effect).

### 👤 swap-face
Replace model faces while preserving clothing and pose.

**Use when**: User wants to change the model's face but keep the outfit and position.

### ✨ retocar
Enhance and retouch product images professionally.

**Use when**: User wants to improve image quality, remove imperfections, or apply professional retouching.

### 🎬 create-video
Animate static product images into videos.

**Use when**: User wants to create dynamic video content from still images.

## Prerequisites

### Required Environment Variable

Set the `VISUALS_API_KEY` environment variable with your master API key:

```bash
export VISUALS_API_KEY="your-master-api-key-here"
```

### Optional API URL

By default, skills use `https://visuals-ai.vercel.app`. To override:

```bash
export VISUALS_API_URL="http://localhost:3000"  # For local testing
```

## Supported Input Types

All skills support three types of image inputs:

1. **Local image files** - PNG, JPG, JPEG (auto-resized if >7MB)
2. **Shopify product URLs** - Fetches available images and lets user choose
3. **Direct image URLs** - Any publicly accessible image URL

## How It Works

### For Shopify Product URLs

1. Fetch available product images
2. Show thumbnails to user for selection
3. Upload selected image to get fal.ai URL
4. Execute workflow with the uploaded URL
5. Poll for completion and return result

### For Local Files

1. Check file size (auto-resize if >7MB to avoid 10MB payload limit)
2. Convert to base64 data URL
3. Execute workflow with data URL
4. Poll for completion and return result

### For Direct URLs

1. Use URL directly in workflow
2. Poll for completion and return result

## Key Features

- **Auto-resize**: Images >7MB are automatically resized to 1024px width
- **Robust polling**: Monitors job status with proper timeout handling
- **Error handling**: Clear error messages and troubleshooting guidance
- **Shopify integration**: Smart product image fetching and upload

## Best Practices

See `BEST_PRACTICES.md` for implementation details including:
- Image size handling and resize logic
- JSON payload construction using Node.js
- Proper polling loop implementation
- Environment variable expansion

## API Documentation

For complete API documentation, see the main Visuals AI repository:
- [AI Integration Guide](https://github.com/Visuals-AI/visuals-ai/blob/main/AI_INTEGRATION.md)
- [API Documentation](https://github.com/Visuals-AI/visuals-ai/blob/main/docs/visuals/API.md)
- [Master Key Guide](https://github.com/Visuals-AI/visuals-ai/blob/main/MASTER_SERVICE_KEY_GUIDE.md)

## Example Usage

### With Claude Code

```bash
# Set environment variable
export VISUALS_API_KEY="your-master-api-key"

# Start Claude Code
claude-code

# Use a skill
/change-color /path/to/image.jpg #FF0000 "Change dress to red"
```

### With Shopify URLs

```
Change this dress to blue: https://www.zenoficial.com.br/products/vestido-midi-fluido
```

Claude will:
1. Fetch the product images
2. Show you thumbnails and ask which to use
3. Upload your selection
4. Execute the color change workflow
5. Show you the result

## Troubleshooting

### "Authentication required" error
- Make sure `VISUALS_API_KEY` is set in your environment
- Check it's set: `echo $VISUALS_API_KEY`

### "Connection refused" error
- Make sure the API server is accessible
- Check: `curl https://visuals-ai.vercel.app/api/workflow/list`

### "Image too large" errors
- Skills auto-resize images >7MB
- Make sure `sips` (macOS) or `convert` (ImageMagick) is installed

## Rate Limits

- **Master API Key**: 100 requests/minute
- **Workflow execution**: No artificial rate limits (fal.ai billing applies)
- **Status polling**: Checks every 3 seconds, max 60 seconds

## Technical Details

- **Payload limit**: 10MB (base64 encoding adds ~33% overhead)
- **Auto-resize threshold**: 7MB (ensures <10MB after encoding)
- **Default model**: `fal-ai/nano-banana-pro/edit`
- **Processing time**: Usually 15-30 seconds for image workflows

## License

See the main Visuals AI repository for license information.
