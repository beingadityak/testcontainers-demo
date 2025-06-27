import base64
import requests
import click
import json
from dnslib import DNSRecord, QTYPE

@click.command()
@click.argument('domain')
@click.option('--url', default='http://127.0.0.1:5000/dns/queries', help='DNS API server URL')
@click.option('--qtype', default='A', help='DNS query type (A, AAAA, MX, etc.)')
def query(domain, url, qtype):
    """Send a DNS query for DOMAIN to the API server and print the response."""
    # Build and encode DNS query
    q = DNSRecord.question(domain, qtype=QTYPE.get(qtype.upper()))
    raw = q.pack()
    base64_query = base64.b64encode(raw).decode('utf-8')

    headers = {"Content-Type": "text/plain"}
    resp = requests.post(url, data=base64_query, headers=headers)

    # Output status
    click.echo(f"\nStatus: {resp.status_code}\n")

    # Output response headers
    click.echo("Headers:")
    for key, value in resp.headers.items():
        click.echo(f"  {key}: {value}")

    # Output response body
    click.echo("\nResponse Body:")
    try:
        parsed_json = resp.json()
        click.echo(json.dumps(parsed_json, indent=2))
    except ValueError:
        click.echo(f"Error: {e}", err=True)

if __name__ == '__main__':
    query()

