# OAuth Testing Tools CLI

A command-line tool for performing OAuth testing against authorization servers. Only supports OAuth2.0 at the moment.

## Installation

```bash
uv sync
```

## Usage

```bash
uv run oauth-dcr --auth-server <AUTH_SERVER_URL> --client-name <CLIENT_NAME> --redirect-uris <REDIRECT_URI_LIST>
```

### Required Arguments

- `--auth-server`: OAuth authorization server URL (e.g., `https://auth.example.com`)
- `--client-name`: Name for the OAuth client
- `--redirect-uris`: Comma-separated list of redirect URIs (e.g., `http://localhost:8080/callback,http://localhost:3000/auth`)

### Example

```bash
uv run oauth-dcr \
  --auth-server https://auth.example.com \
  --client-name "My OAuth2 Client" \
  --redirect-uris "http://localhost:8080/callback,http://localhost:3000/auth"
```

## Features

- Automatic discovery of registration endpoint via `.well-known/oauth-authorization-server`
- Dynamic client registration following RFC 7591
- Pretty-printed JSON responses
- Comprehensive error handling
- No PKCE support (as requested)

## How It Works

1. The tool discovers the authorization server's metadata using the `.well-known` endpoint
2. Extracts the `registration_endpoint` from the metadata
3. Registers a new client with the provided name and redirect URIs
4. Displays the complete registration response including `client_id` and `client_secret`

## Error Handling

The tool gracefully handles:

- Network connection errors
- Invalid JSON responses
- Registration errors with detailed error codes and descriptions
- Missing registration endpoint (server doesn't support dynamic registration)
