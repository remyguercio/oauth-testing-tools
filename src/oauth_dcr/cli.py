#!/usr/bin/env python3
import asyncio
import json
import sys
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, urlparse

import click
import httpx
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.text import Text

console = Console()


async def discover_registration_endpoint(auth_server: str) -> Optional[str]:
    """
    Discover the registration endpoint using .well-known OAuth authorization server metadata.
    
    Args:
        auth_server: The OAuth2 authorization server URL
        
    Returns:
        The registration endpoint URL if found, None otherwise
    """
    # Ensure the auth_server has a scheme
    parsed = urlparse(auth_server)
    if not parsed.scheme:
        auth_server = f"https://{auth_server}"
    
    # Construct the .well-known URL
    well_known_url = urljoin(auth_server, "/.well-known/oauth-authorization-server")
    
    console.print(f"[cyan]Discovering OAuth2 metadata from:[/cyan] {well_known_url}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(well_known_url, follow_redirects=True)
            response.raise_for_status()
            
            metadata = response.json()
            console.print("\n[green]Successfully retrieved authorization server metadata:[/green]")
            console.print(Panel(JSON.from_data(metadata), title="Authorization Server Metadata"))
            
            registration_endpoint = metadata.get("registration_endpoint")
            if not registration_endpoint:
                console.print("\n[yellow]Warning:[/yellow] This authorization server does not support dynamic client registration.")
                console.print("No 'registration_endpoint' found in the metadata.")
                return None
                
            return registration_endpoint
            
        except httpx.HTTPStatusError as e:
            console.print(f"\n[red]Error:[/red] Failed to retrieve metadata: HTTP {e.response.status_code}")
            console.print(f"Response: {e.response.text}")
            return None
        except httpx.RequestError as e:
            console.print(f"\n[red]Error:[/red] Failed to connect to authorization server: {e}")
            return None
        except json.JSONDecodeError:
            console.print("\n[red]Error:[/red] Invalid JSON response from authorization server")
            return None


async def register_client(registration_endpoint: str, client_name: str, redirect_uris: List[str]) -> Dict[str, Any]:
    """
    Register a new OAuth2 client using dynamic client registration.
    
    Args:
        registration_endpoint: The registration endpoint URL
        client_name: The name for the client
        redirect_uris: List of redirect URIs for the client
        
    Returns:
        The registration response data
    """
    registration_request = {
        "client_name": client_name,
        "redirect_uris": redirect_uris,
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "client_secret_basic"
    }
    
    console.print(f"\n[cyan]Registering client at:[/cyan] {registration_endpoint}")
    console.print("[cyan]Registration request:[/cyan]")
    console.print(Panel(JSON.from_data(registration_request), title="Client Registration Request"))
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                registration_endpoint,
                json=registration_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                registration_response = response.json()
                console.print("\n[green]✓ Client registered successfully![/green]")
                console.print("\n[cyan]Registration response:[/cyan]")
                console.print(Panel(JSON.from_data(registration_response), title="Client Registration Response"))
                return registration_response
            else:
                # Handle error response
                try:
                    error_data = response.json()
                    error = error_data.get("error", "unknown_error")
                    error_description = error_data.get("error_description", "No description provided")
                    
                    console.print(f"\n[red]Registration failed with error:[/red] {error}")
                    console.print(f"[red]Description:[/red] {error_description}")
                    console.print(f"\n[dim]HTTP Status:[/dim] {response.status_code}")
                    console.print(Panel(JSON.from_data(error_data), title="Error Response", border_style="red"))
                except json.JSONDecodeError:
                    console.print(f"\n[red]Registration failed:[/red] HTTP {response.status_code}")
                    console.print(f"Response: {response.text}")
                
                sys.exit(1)
                
        except httpx.RequestError as e:
            console.print(f"\n[red]Error:[/red] Failed to connect to registration endpoint: {e}")
            sys.exit(1)
        except json.JSONDecodeError:
            console.print("\n[red]Error:[/red] Invalid JSON response from registration endpoint")
            sys.exit(1)


@click.command()
@click.option(
    "--auth-server",
    required=True,
    help="OAuth2 authorization server URL"
)
@click.option(
    "--client-name",
    required=True,
    help="Name for the OAuth2 client"
)
@click.option(
    "--redirect-uris",
    required=True,
    help="Comma-separated list of redirect URIs (e.g., http://localhost:8080/callback,http://localhost:3000/auth)"
)
def main(auth_server: str, client_name: str, redirect_uris: str):
    """
    OAuth2 Dynamic Client Registration CLI
    
    This tool performs dynamic client registration against an OAuth2 authorization
    server following RFC 7591. It discovers the registration endpoint using the
    .well-known OAuth authorization server metadata.
    """
    # Parse redirect URIs
    redirect_uri_list = [uri.strip() for uri in redirect_uris.split(",") if uri.strip()]
    
    if not redirect_uri_list:
        console.print("[red]Error:[/red] At least one redirect URI must be provided")
        sys.exit(1)
    
    console.print(Panel.fit(
        "[bold cyan]OAuth2 Dynamic Client Registration[/bold cyan]\n"
        f"Server: {auth_server}\n"
        f"Client Name: {client_name}\n"
        f"Redirect URIs: {', '.join(redirect_uri_list)}",
        title="Configuration"
    ))
    
    # Run the async functions
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Discover registration endpoint
        registration_endpoint = loop.run_until_complete(
            discover_registration_endpoint(auth_server)
        )
        
        if not registration_endpoint:
            console.print("\n[red]Error:[/red] Unable to find registration endpoint")
            sys.exit(1)
        
        # Register the client
        loop.run_until_complete(
            register_client(registration_endpoint, client_name, redirect_uri_list)
        )
        
    finally:
        loop.close()


if __name__ == "__main__":
    main()