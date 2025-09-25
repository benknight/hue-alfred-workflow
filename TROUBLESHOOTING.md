# Troubleshooting Hue Bridge Connectivity

This document helps resolve common issues when connecting to different types of Hue bridges, including the Hue Bridge Pro.

## Common Issues and Solutions

### Issue: "Cannot connect to Hue Bridge Pro"

The Hue Bridge Pro may use slightly different API response formats compared to older bridges. This workflow now includes enhanced compatibility.

**Solution:**
1. First try the automatic setup: `hue` (press Enter on "Link with Hue bridge")
2. If that fails, try manual IP setup: `hue 192.168.1.100` (replace with your bridge's IP)
3. Make sure to press the physical button on your bridge within 30 seconds of running the setup

### Issue: "No bridges found on your network"

**Troubleshooting steps:**
1. **Check network connection**: Ensure your Mac and Hue bridge are on the same network
2. **Find bridge IP manually**: 
   - Open the Hue app on your phone
   - Go to Settings → Hue bridges → (i) icon next to your bridge
   - Note the IP address and use it manually: `hue 192.168.1.100`
3. **Check firewall**: Ensure your Mac's firewall isn't blocking the discovery request
4. **Router issues**: Some routers block mDNS discovery. Use manual IP setup as workaround.

### Issue: "Setup Error: Press the button on your Hue bridge and try again"

This is normal behavior for security. The Hue bridge requires physical access to authorize new applications.

**Solution:**
1. Press and release the large button on top of your Hue bridge
2. Within 30 seconds, run the setup again in Alfred
3. If using manual IP: `hue 192.168.1.100` (after pressing button)

### Issue: "Bridge returned error" or data format errors

This can happen with newer bridge firmware or different bridge models.

**Troubleshooting:**
1. **Try manual IP setup** instead of auto-discovery
2. **Reset workflow data**: Type `hue workflow:reset` (don't press Enter, just typing it will reset)
3. **Check bridge firmware**: Ensure your bridge firmware is up to date via the Hue app
4. **Check Alfred logs**: Look for specific error messages in Alfred's debugger

### Issue: Workflow shows "Error in workflow 'Philips Hue Controller'"

**Solution:**
1. **Reset workflow**: `hue workflow:reset`
2. **Restart Alfred**: Quit and restart Alfred app
3. **Re-run setup**: Follow the setup process again
4. **Check logs**: Enable Alfred's debugger to see detailed error messages

## Bridge Type Compatibility

This workflow supports multiple bridge types:

- **Philips Hue Bridge (all generations)** ✅
- **Philips Hue Bridge Pro** ✅  
- **deCONZ bridge** ✅
- **HomeKit-compatible bridges** ✅

## Manual Setup Process

If automatic discovery fails:

1. **Find your bridge IP**:
   - Use the Hue app: Settings → Hue bridges → (i) icon
   - Or check your router's connected devices list
   - Or use network scanner apps

2. **Run manual setup**:
   ```
   hue 192.168.1.100  (replace with your actual IP)
   ```

3. **Press bridge button**: Physical button on bridge within 30 seconds

4. **Complete setup**: You should see "Success!" message

## Getting Help

If you're still experiencing issues:

1. **Enable Alfred Debugger**:
   - Alfred Preferences → Workflows → Philips Hue Controller
   - Click the bug icon (🐛) in the top right
   - Try the failing action and copy the error details

2. **Check workflow version**: Ensure you have the latest version with Hue Bridge Pro support

3. **Reset and retry**: Use `hue workflow:reset` to start fresh

4. **Bridge-specific notes**:
   - **Hue Bridge Pro**: May take longer to respond, be patient during setup
   - **deCONZ**: Scene management works differently but is supported
   - **HomeKit bridges**: Some features may be limited

## Advanced Troubleshooting

### Check Bridge Response Format
The workflow now handles multiple response formats, but if you're curious about what your bridge returns:

1. Find your bridge IP and username (after successful setup)
2. Open Terminal and run:
   ```bash
   curl http://YOUR_BRIDGE_IP/api/YOUR_USERNAME
   ```
3. This shows the raw data structure your bridge provides

### Common Error Patterns

- **"list indices must be integers"**: Fixed in latest version, update workflow
- **"unauthorized user"**: Re-run setup with button press
- **"resource not available"**: Bridge may be rebooting, wait and retry
- **Connection timeout**: Check network connectivity

This enhanced version should work with Hue Bridge Pro and provide better error messages for debugging any remaining issues.