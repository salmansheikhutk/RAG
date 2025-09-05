# Product Manual - XR-450 Industrial Controller

## Overview
The XR-450 is a high-performance industrial controller designed for automation and process control applications.

## Specifications

### Power Requirements
- Input Voltage: 24V DC ±10%
- Power Consumption: 12W typical, 15W maximum
- Power Input: 2-pin terminal block

### Physical Specifications
- Dimensions: 120mm × 80mm × 45mm
- Weight: 350g
- Operating Temperature: -20°C to +60°C
- Storage Temperature: -40°C to +85°C
- Humidity: 5-95% RH (non-condensing)

### Communication Interfaces
- Ethernet: 10/100 Mbps
- RS-485: Up to 115.2k baud
- USB: USB 2.0 for configuration
- Digital I/O: 16 inputs, 12 outputs

## Installation

### Safety Precautions
⚠️ **WARNING**: Always disconnect power before installation or maintenance.

### Mounting Instructions
1. Select a suitable location with adequate ventilation
2. Mount using the provided DIN rail clip or panel mount brackets
3. Ensure minimum 50mm clearance on all sides for cooling
4. Connect to properly grounded power supply

### Wiring
1. Connect 24V DC power to terminals 1 (+) and 2 (-)
2. Connect Ethernet cable to RJ45 port
3. Wire I/O connections according to application requirements
4. Verify all connections before applying power

## Configuration

### Initial Setup
1. Connect via Ethernet using IP address 192.168.1.100 (default)
2. Open web browser and navigate to controller IP
3. Login with default credentials (admin/admin)
4. Change default password for security

### Network Configuration
- Set static IP address for your network
- Configure subnet mask and gateway
- Enable DHCP if required
- Test network connectivity

## Troubleshooting

### Common Error Codes

#### E404 - Communication Timeout
**Symptoms**: Loss of communication with field devices
**Causes**: 
- Network cable disconnected
- Incorrect network settings
- Device power failure
**Solutions**:
1. Check all network connections
2. Verify IP address configuration
3. Test with ping command
4. Check device power status
5. Reset network settings if necessary

#### E501 - Power Supply Error
**Symptoms**: Controller fails to start or operates erratically
**Causes**:
- Input voltage out of range
- Power supply overload
- Faulty power connection
**Solutions**:
1. Measure input voltage (must be 21.6V - 26.4V)
2. Check power supply capacity
3. Inspect terminal connections
4. Replace power supply if faulty

#### E203 - I/O Module Fault
**Symptoms**: Digital inputs/outputs not responding
**Causes**:
- Faulty I/O module
- Incorrect wiring
- Overload condition
**Solutions**:
1. Check I/O wiring against schematic
2. Verify load current within specifications
3. Test continuity of I/O connections
4. Replace I/O module if defective

### LED Status Indicators
- **PWR (Green)**: Power applied and system OK
- **RUN (Green)**: Controller running normally
- **ERR (Red)**: System error - check error codes
- **COMM (Yellow)**: Communication activity

## Maintenance

### Routine Maintenance
- Clean air vents monthly
- Check terminal tightness quarterly
- Update firmware as recommended
- Back up configuration regularly

### Firmware Updates
1. Download latest firmware from support website
2. Connect via USB or Ethernet
3. Use firmware update utility
4. Do not power off during update process

## Technical Support
For additional support, contact:
- Technical Support: 1-800-TECH-HELP
- Email: support@company.com
- Website: www.company.com/support

## Compliance and Certifications
- CE Marking: Compliant with EMC Directive 2014/30/EU
- UL Listed: UL 508 Industrial Control Equipment
- FCC Part 15: Class A digital device
- RoHS Compliant: Lead-free construction

## Warranty
2-year limited warranty from date of purchase. See warranty terms at www.company.com/warranty
