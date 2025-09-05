# API Documentation - XR Series Controllers

## Overview
The XR Series controllers provide a comprehensive REST API for integration with enterprise systems, SCADA applications, and custom automation solutions.

## Base URL
```
https://{controller_ip}/api/v1/
```

## Authentication
All API calls require authentication using API tokens.

### Getting an API Token
```http
POST /auth/token
Content-Type: application/json

{
    "username": "admin",
    "password": "your_password"
}
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 3600
}
```

### Using the Token
Include the token in the Authorization header:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## System Information

### Get System Status
```http
GET /system/status
```

**Response:**
```json
{
    "system_status": "online",
    "cpu_usage": 15.2,
    "memory_usage": 45.8,
    "uptime": 8765432,
    "temperature": 42.5,
    "firmware_version": "2.1.4"
}
```

### Get System Configuration
```http
GET /system/config
```

**Response:**
```json
{
    "device_name": "XR450-Production",
    "ip_address": "192.168.1.100",
    "subnet_mask": "255.255.255.0",
    "gateway": "192.168.1.1",
    "dns_servers": ["8.8.8.8", "8.8.4.4"],
    "ntp_server": "pool.ntp.org"
}
```

## I/O Operations

### Read Digital Inputs
```http
GET /io/digital/inputs
```

**Response:**
```json
{
    "inputs": {
        "DI1": true,
        "DI2": false,
        "DI3": true,
        "DI4": false
    },
    "timestamp": "2024-09-05T14:30:00Z"
}
```

### Control Digital Outputs
```http
POST /io/digital/outputs
Content-Type: application/json

{
    "DO1": true,
    "DO2": false,
    "DO3": true
}
```

### Read Analog Values
```http
GET /io/analog/inputs
```

**Response:**
```json
{
    "inputs": {
        "AI1": {
            "value": 4.567,
            "unit": "V",
            "range": "0-10V"
        },
        "AI2": {
            "value": 12.345,
            "unit": "mA",
            "range": "4-20mA"
        }
    }
}
```

## Data Logging

### Get Historical Data
```http
GET /data/history?start=2024-09-01T00:00:00Z&end=2024-09-05T23:59:59Z&points=DI1,AI1
```

**Parameters:**
- `start`: Start timestamp (ISO 8601)
- `end`: End timestamp (ISO 8601)
- `points`: Comma-separated list of data points

**Response:**
```json
{
    "data": [
        {
            "timestamp": "2024-09-01T00:00:00Z",
            "DI1": true,
            "AI1": 5.234
        },
        {
            "timestamp": "2024-09-01T00:01:00Z", 
            "DI1": false,
            "AI1": 5.267
        }
    ],
    "total_records": 7200
}
```

## Alarms and Events

### Get Active Alarms
```http
GET /alarms/active
```

**Response:**
```json
{
    "alarms": [
        {
            "id": "ALM001",
            "severity": "HIGH", 
            "message": "Temperature sensor fault",
            "timestamp": "2024-09-05T14:25:30Z",
            "acknowledged": false
        }
    ]
}
```

### Acknowledge Alarm
```http
POST /alarms/{alarm_id}/acknowledge
Content-Type: application/json

{
    "user": "operator1",
    "comment": "Investigating temperature sensor"
}
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error information.

### Error Response Format
```json
{
    "error": {
        "code": "INVALID_PARAMETER",
        "message": "The specified I/O point does not exist",
        "details": {
            "parameter": "point_id",
            "provided_value": "DI99"
        }
    }
}
```

### Common Error Codes
- `400 Bad Request`: Invalid request format or parameters
- `401 Unauthorized`: Invalid or expired authentication token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting
- Maximum 1000 requests per hour per API token
- Burst limit of 10 requests per second
- Rate limit headers included in responses:
  ```
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 995
  X-RateLimit-Reset: 1694008800
  ```

## WebSocket Support

### Real-time Data Stream
```javascript
const ws = new WebSocket('wss://controller_ip/api/v1/stream');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Real-time data:', data);
};
```

### Subscribe to Data Points
```json
{
    "action": "subscribe",
    "points": ["DI1", "DI2", "AI1", "AI2"],
    "interval": 1000
}
```

## SDK and Libraries

### Python SDK
```python
from xr_controller import XRController

controller = XRController('192.168.1.100', api_token='your_token')
status = controller.get_system_status()
inputs = controller.read_digital_inputs()
controller.set_digital_output('DO1', True)
```

### JavaScript SDK
```javascript
import { XRController } from 'xr-controller-js';

const controller = new XRController('192.168.1.100', {
    token: 'your_token'
});

const status = await controller.getSystemStatus();
const inputs = await controller.readDigitalInputs();
await controller.setDigitalOutput('DO1', true);
```

## Best Practices

### Performance Optimization
- Use batch operations when possible
- Implement proper caching for frequently accessed data
- Use WebSocket for real-time data instead of polling

### Security Recommendations
- Rotate API tokens regularly
- Use HTTPS for all communications
- Implement proper access controls
- Monitor API usage for anomalies

### Integration Guidelines
- Handle network timeouts gracefully
- Implement retry logic with exponential backoff
- Log API interactions for debugging
- Validate all responses before processing

## Support

For API support:
- Documentation: https://docs.company.com/api
- Support Email: api-support@company.com
- Developer Forum: https://forum.company.com/api
