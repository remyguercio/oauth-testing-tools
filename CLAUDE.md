# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an OAuth Testing Tools CLI project that provides command-line utilities for testing OAuth2.0 authorization servers. Currently, it implements OAuth2 Dynamic Client Registration (DCR) following RFC 7591.

## Development Setup

### Install Dependencies
```bash
uv sync
```

### Run the CLI Tool
```bash
uv run oauth-dcr --auth-server <server> --client-name <name> --redirect-uris <uri1,uri2>
```

### Development Commands
- Run without installation: `PYTHONPATH=src uv run python -m oauth_dcr.cli --help`
- Reinstall after changes: `uv sync`

## Architecture

### Package Structure
- `src/oauth_dcr/`: Main package directory
  - `cli.py`: Click-based CLI implementation with async OAuth2 DCR logic

### Key Design Decisions
1. **Async HTTP**: Uses httpx for async HTTP requests to handle OAuth2 server communication efficiently
2. **Rich Output**: Uses the rich library for formatted, colored console output
3. **Error Handling**: Comprehensive error handling for network issues, invalid JSON, and OAuth2-specific errors
4. **No PKCE Support**: Intentionally omitted as per requirements

### OAuth2 DCR Implementation Details
The tool follows this flow:
1. Discovers the registration endpoint via `.well-known/oauth-authorization-server` metadata (RFC 8414)
2. Sends a registration request with client metadata (RFC 7591)
3. Handles both successful registrations (201) and error responses (400)

### Important Considerations
- The tool automatically prepends `https://` if no scheme is provided in the auth-server URL
- Redirect URIs are passed as a comma-separated list and parsed into an array
- The registration request includes fixed grant types and response types for authorization code flow
- All responses are displayed with JSON formatting for clarity

## Future Extensions
When adding new OAuth testing tools:
1. Create new modules under `src/oauth_<feature>/`
2. Add corresponding CLI commands to `[project.scripts]` in pyproject.toml
3. Follow the same async pattern and error handling approach
4. Use rich for consistent output formatting