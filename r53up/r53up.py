# Copyright (c) 2019 Ben Ransford.
"""Update a DNS entry in Route53 with my IP address."""

import http.client
import logging
import json
from os import getuid
from pwd import getpwuid
from socket import gethostname
import urllib
import boto3
import click
from . import __version__


APIFY4 = 'https://api.ipify.org?format=json'
APIFY6 = 'https://api6.ipify.org?format=json'
CLIENT_USERNAME = getpwuid(getuid())[0]
CLIENT_HOSTNAME = gethostname()
logger = logging.getLogger(__name__)


def get_ip_address(url: str) -> str:
    """Get my IP address from a JSON API endpoint.

    The API endpoint should return an object like this:

        {ip: 'string'}
    """
    ip_response = urllib.request.urlopen(url)
    jj = json.loads(ip_response.read())
    return jj['ip']


def get_ipv4_address() -> str:
    """Get an IPv4 address from a JSON API endpoint."""
    ip = get_ip_address(APIFY4)
    logger.info('My IPv4 address: %s', ip)
    return ip


def get_ipv6_address() -> str:
    """Get an IPv6 address from a JSON API endpoint."""
    ip = get_ip_address(APIFY6)
    if ':' in ip:
        logger.info('My IPv6 address: %s', ip)
        return ip
    return ''


def get_change_record(hostname: str, addr: str, rrtype: str):
    """Return a Route 53 request to UPSERT a resource record.

    As documented in
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/ \
        services/route53.html#Route53.Client.change_resource_record_sets
    """
    assert rrtype in ('A', 'AAAA')
    return {
        'Action': 'UPSERT',
        'ResourceRecordSet': {
            'Name': hostname,
            'Type': rrtype,
            'TTL': 60,
            'ResourceRecords': [{'Value': addr}]
        }
    }


class UpdateError(Exception):
    """An error representing a failure to update a Route 53 entry."""
    pass


def do_update_ip(zone_id: str, hostname: str):
    """Update an IP address.

    Raises a descriptive UpdateError upon any failure.
    """
    try:
        ipv4 = get_ipv4_address()
        ipv6 = get_ipv6_address()
    except (http.client.HTTPException, urllib.error.URLError) as e:
        raise UpdateError('Failed to get IP address') from e

    comment = '{}@{} via {}'.format(
        CLIENT_USERNAME,
        CLIENT_HOSTNAME,
        __file__
    )

    changes = [get_change_record(hostname, ipv4, 'A')]
    if ipv6:
        changes.append(get_change_record(hostname, ipv6, 'AAAA'))
    logger.info('Submitting %d change(s)', len(changes))

    client = boto3.client('route53')
    try:
        ret = client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch={
                'Comment': comment,
                'Changes': changes
            }
        )
        logger.info('AWS responded: %s', ret)
    except client.exceptions.InvalidChangeBatch:
        raise UpdateError('Change rejected') from e


def init_logger(verbose: bool):
    """Initializes logging."""
    log_level = logging.INFO if verbose else logging.WARNING
    log_format = '%(asctime)s %(name)s: %(levelname)s: %(message)s'
    formatter = logging.Formatter(log_format)
    stderr = logging.StreamHandler()
    stderr.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers = [stderr]


@click.command()
@click.argument('aws_zone_id', type=str)
@click.argument('hostname', type=str)
@click.option('-v', '--verbose', is_flag=True, default=False,
              help='Verbose output')
@click.option('-V', '--version', is_flag=True, default=False,
              help='Show version information and exit.')
def main(aws_zone_id, hostname, verbose, version):
    """Main function."""
    if version:
        print(__version__)
        return 0

    init_logger(verbose)

    try:
        do_update_ip(aws_zone_id, hostname)
    except UpdateError:
        logger.exception('Update failed')
        return 1
    return 0
