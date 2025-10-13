# REST Adapter Token Authentication

The REST adapter now supports multiple authentication methods, including token-based authentication with environment variable support for secure credential management in development and CI/CD environments.

## Supported Authentication Methods

### 1. Basic Authentication (Backward Compatible)

```python
from data_agents.adapters.rest_adapter import RESTAdapter

# Tuple format (original)
config = {
    "auth": ("username", "password")
}

# Dict format  
config = {
    "auth": {
        "type": "basic",
        "username": "your_username",
        "password": "your_password"
    }
}

adapter = RESTAdapter("https://api.example.com", config)
```

### 2. Bearer Token Authentication

```python
# Simple string format (auto-detected as bearer token)
config = {
    "auth": "your-bearer-token-here"
}

# Explicit dict format
config = {
    "auth": {
        "type": "bearer",
        "token": "your-bearer-token-here"
    }
}

# From environment variable
config = {
    "auth": {
        "type": "bearer",
        "env_var": "BEARER_TOKEN"
    }
}

adapter = RESTAdapter("https://api.example.com", config)
```

### 3. API Key Authentication

```python
# Default API key header (X-API-Key)
config = {
    "auth": {
        "type": "api_key",
        "token": "your-api-key-here"
    }
}

# Custom header name
config = {
    "auth": {
        "type": "api_key",
        "key": "X-Custom-API-Key",
        "token": "your-api-key-here"
    }
}

# From environment variable
config = {
    "auth": {
        "type": "api_key",
        "key": "X-API-Key",
        "env_var": "API_KEY"
    }
}

adapter = RESTAdapter("https://api.example.com", config)
```

### 4. Environment Variable References

You can reference environment variables in string tokens using `${VAR_NAME}` syntax:

```python
config = {
    "auth": "${MY_API_TOKEN}"  # Automatically treated as bearer token
}

adapter = RESTAdapter("https://api.example.com", config)
```

## Local Development Setup

For local development, set environment variables in your shell:

```bash
# Set API key for local testing
export OPENAQ_API_KEY="your-actual-api-key"
export BEARER_TOKEN="your-bearer-token"

# Run your script
python your_script.py
```

Or use a `.env` file with python-dotenv:

```python
from dotenv import load_dotenv
load_dotenv()

# Now environment variables are loaded
config = {
    "auth": {
        "type": "api_key",
        "key": "X-API-Key",
        "env_var": "OPENAQ_API_KEY"
    }
}
```

## GitHub Actions Integration

Set up secrets in your GitHub repository and reference them in workflows:

### Setting Repository Secrets

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add secrets like `OPENAQ_API_KEY`, `BEARER_TOKEN`, etc.

### Workflow Configuration

```yaml
name: Data Collection with API Authentication

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 */6 * * *'  # Run every 6 hours

jobs:
  collect-data:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
    
    - name: Collect OpenAQ data
      env:
        OPENAQ_API_KEY: ${{ secrets.OPENAQ_API_KEY }}
      run: |
        python -c "
        from data_agents.adapters.rest_adapter import RESTAdapter
        
        config = {
            'auth': {
                'type': 'api_key',
                'key': 'X-API-Key',
                'env_var': 'OPENAQ_API_KEY'
            }
        }
        
        adapter = RESTAdapter('https://api.openaq.org/v2', config)
        countries = adapter.query('countries', params={'limit': 10})
        print(f'Retrieved data for {len(countries)} countries')
        "
    
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: api-data
        path: data/
```

## Configuration Examples

### OpenAQ API Configuration

```json
{
    "name": "OpenAQ API",
    "description": "Air quality data from OpenAQ API",
    "adapter_type": "rest",
    "base_url": "https://api.openaq.org/v2",
    "config": {
        "auth": {
            "type": "api_key",
            "key": "X-API-Key",
            "env_var": "OPENAQ_API_KEY"
        },
        "headers": {
            "Accept": "application/json",
            "User-Agent": "data-agents/1.0"
        },
        "timeout": 30
    }
}
```

### Multiple Service Configuration

```python
# Different auth methods for different services
configs = {
    "openaq": {
        "base_url": "https://api.openaq.org/v2",
        "config": {
            "auth": {
                "type": "api_key",
                "key": "X-API-Key", 
                "env_var": "OPENAQ_API_KEY"
            }
        }
    },
    "bearer_service": {
        "base_url": "https://api.example.com",
        "config": {
            "auth": {
                "type": "bearer",
                "env_var": "BEARER_TOKEN"
            }
        }
    },
    "basic_auth_service": {
        "base_url": "https://legacy-api.example.com",
        "config": {
            "auth": ("username", "password")
        }
    }
}

# Create adapters for each service
adapters = {
    name: RESTAdapter(conf["base_url"], conf["config"])
    for name, conf in configs.items()
}
```

## Error Handling

The adapter will raise descriptive errors for common authentication issues:

```python
try:
    adapter = RESTAdapter("https://api.example.com", {
        "auth": {
            "type": "bearer",
            "env_var": "MISSING_TOKEN"
        }
    })
except ValueError as e:
    print(f"Authentication error: {e}")
    # Output: Authentication error: Environment variable 'MISSING_TOKEN' not found
```

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive credentials
3. **Set up GitHub secrets** for CI/CD workflows
4. **Rotate tokens regularly** and update secrets accordingly
5. **Use least-privilege principles** - only grant necessary API permissions
6. **Monitor API usage** to detect unauthorized access

## Testing

Run the authentication examples to verify your setup:

```bash
# Test all auth methods
OPENAQ_API_KEY="your-key" python examples/token_auth_example.py

# Run the test suite
python -m pytest tests/adapters/test_rest_adapter_auth.py -v
```

## Migration from Basic Auth

If you're currently using basic authentication, the new token support is fully backward compatible:

```python
# Old way (still works)
config = {"auth": ("username", "password")}

# New way (same functionality)
config = {
    "auth": {
        "type": "basic",
        "username": "username", 
        "password": "password"
    }
}

# Both create the same adapter behavior
```