# Cheating Event API

## Endpoint

`POST /api/cheating-events`

## Description

This endpoint allows you to upload an image and record a cheating event with a student's name.

## Request

### Headers
- `Content-Type: multipart/form-data`
- `Accept: application/json`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Student's name (max 255 characters) |
| `image` | file | Yes | Image file (JPEG, PNG, JPG, GIF, SVG, max 2MB) |

### Example Request (using cURL)

```bash
curl -X POST http://your-domain.com/api/cheating-events \
  -H "Accept: application/json" \
  -F "name=John Doe" \
  -F "image=@/path/to/image.jpg"
```

### Example Request (using JavaScript/Fetch)

```javascript
const formData = new FormData();
formData.append('name', 'John Doe');
formData.append('image', imageFile); // File object from input

fetch('/api/cheating-events', {
    method: 'POST',
    headers: {
        'Accept': 'application/json',
        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content // If using CSRF protection
    },
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## Response

### Success Response (201 Created)

```json
{
    "success": true,
    "message": "Cheating event recorded successfully",
    "data": {
        "id": 1,
        "name": "John Doe",
        "image": "cheating-events/abc123.jpg",
        "image_url": "http://your-domain.com/storage/cheating-events/abc123.jpg",
        "created_at": "2025-06-04T10:30:00.000000Z"
    }
}
```

### Validation Error Response (422 Unprocessable Entity)

```json
{
    "success": false,
    "message": "Validation failed",
    "errors": {
        "name": ["The name field is required."],
        "image": ["The image field is required."]
    }
}
```

### Server Error Response (500 Internal Server Error)

```json
{
    "success": false,
    "message": "Failed to record cheating event",
    "error": "Error details..."
}
```

## File Storage

- Images are stored in `storage/app/public/cheating-events/`
- They are accessible via the public URL: `/storage/cheating-events/{filename}`
- Make sure to run `php artisan storage:link` to create the symbolic link

## Security Notes

- File uploads are validated for type and size
- Only image files are allowed (JPEG, PNG, JPG, GIF, SVG)
- Maximum file size is 2MB
- Consider adding authentication middleware for production use
