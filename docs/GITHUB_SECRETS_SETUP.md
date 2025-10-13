# Setting up GitHub Repository Secrets for OpenAQ API

This guide explains how to configure GitHub repository secrets for OpenAQ API authentication in the data-agents project.

## Overview

The data-agents project includes integration tests that verify token-based authentication with the OpenAQ API. These tests run automatically in GitHub Actions on Ubuntu, macOS, and Windows environments when an `OPENAQ_API_KEY` secret is configured.

## Setting up OpenAQ API Key

### 1. Get an OpenAQ API Key

1. Visit the [OpenAQ API documentation](https://docs.openaq.org/)
2. Sign up for an account or log in
3. Navigate to your API settings/dashboard
4. Generate a new API key for the v3 API
5. Copy the API key (you'll need it in the next step)

### 2. Add Secret to GitHub Repository

1. Go to your GitHub repository (e.g., `https://github.com/your-username/data-agents`)
2. Click on **Settings** (repository settings, not your personal settings)
3. In the left sidebar, click on **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Set the secret details:
   - **Name**: `OPENAQ_API_KEY`
   - **Secret**: Paste your OpenAQ API key here
6. Click **Add secret**

### 3. Verify Setup

Once the secret is added, the GitHub Actions workflows will automatically:

1. **Load the API key** from the `OPENAQ_API_KEY` secret
2. **Run authentication tests** to verify the key works
3. **Test real API calls** to OpenAQ v3 endpoints
4. **Report results** in the workflow logs

## What Gets Tested

The workflows include these OpenAQ-specific tests:

### Authentication Configuration Tests
- ✅ Verify token authentication setup
- ✅ Check HTTP headers are configured correctly
- ✅ Validate REST adapter configuration

### API Integration Tests
- ✅ Test connection to `https://api.openaq.org/v3`
- ✅ Verify API key authentication
- ✅ Test `instruments` endpoint with real data
- ✅ Handle various API response scenarios (rate limits, errors, etc.)

### Error Handling Tests
- ✅ Invalid API keys (401 Unauthorized)
- ✅ Missing API keys (graceful degradation)
- ✅ Rate limiting (429 Too Many Requests)
- ✅ Network timeouts and connectivity issues

## Viewing Test Results

### Successful Run with Valid API Key
```
✓ API key found: abc12345...
✓ Authentication configured correctly
✓ API request successful: 3 instruments retrieved
  Response columns: ['id', 'name', 'isMonitor', 'parameters']
```

### Run without API Key (Expected)
```
⚠ OPENAQ_API_KEY environment variable not set
  This test requires an OpenAQ API key for authentication
  Set the environment variable or configure GitHub secrets
```

### Run with Invalid API Key
```
❌ Authentication failed: Invalid API key
  Check that OPENAQ_API_KEY is set correctly
```

## Local Development

For local testing, you can set the environment variable:

```bash
# Export for your session
export OPENAQ_API_KEY="your-actual-api-key-here"

# Test the integration
python examples/openaq_integration_test.py

# Run the integration tests
pytest tests/integration/test_openaq_auth.py -v
```

## Workflow Integration

The OpenAQ tests are integrated into all three platform workflows:

### Ubuntu (`ubuntu.yml`)
- Runs pytest with coverage
- Executes OpenAQ integration tests
- Runs standalone integration script

### macOS (`mac.yml`)
- Runs pytest suite
- Executes OpenAQ integration tests
- Runs standalone integration script

### Windows (`windows.yml`)
- Runs pytest suite  
- Executes OpenAQ integration tests
- Runs standalone integration script

## Security Notes

- 🔒 **API keys are secure**: GitHub secrets are encrypted and only accessible to workflow runs
- 🔒 **No logs exposure**: API keys are not printed in workflow logs
- 🔒 **Branch protection**: Secrets are only available to workflows on protected branches
- 🔒 **Access control**: Only repository admins can view/modify secrets

## Troubleshooting

### Tests are Skipped
This is normal if the `OPENAQ_API_KEY` secret is not configured. The tests gracefully skip when no API key is available.

### Authentication Failures
1. Verify the API key is correct in GitHub secrets
2. Check that the key has permissions for OpenAQ v3 API
3. Ensure the key hasn't expired or been revoked

### Rate Limiting
If you see 429 errors, the API key is working but hitting rate limits. This is expected for high-frequency testing and doesn't indicate a problem.

### API Timeouts
Occasional timeouts are normal and tests are designed to handle them gracefully. Persistent timeouts may indicate API availability issues.

## Example Configuration Files

### OpenAQ Adapter Config (`config/openaq.adapter.json`)
```json
{
    "name": "OpenAQ API v3",
    "base_url": "https://api.openaq.org/v3",
    "config": {
        "auth": {
            "type": "api_key",
            "key": "X-API-Key",
            "env_var": "OPENAQ_API_KEY"
        }
    }
}
```

### Local Testing Script
```python
from data_agents.adapters.rest_adapter import RESTAdapter

config = {
    "auth": {
        "type": "api_key",
        "key": "X-API-Key", 
        "env_var": "OPENAQ_API_KEY"
    }
}

adapter = RESTAdapter("https://api.openaq.org/v3", config)
result = adapter.query("instruments", params={"limit": 5})
print(f"Retrieved {len(result)} instruments")
```