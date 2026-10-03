"""Passive destination inspection; this module makes no network requests."""
import ipaddress
import re
from urllib.parse import urlsplit, parse_qs
from .schema import Destination, Identity

SHORTENERS = {'bit.ly', 't.co', 'tinyurl.com', 'goo.gl', 'is.gd', 'cutt.ly'}


def inspect(value, page, bbox=None, confidence=1.0):
    concerns = []
    try:
        parsed = urlsplit('https://' + value if value.startswith('www.') else value)
        host = (parsed.hostname or '').lower().rstrip('.')
        payee = parse_qs(parsed.query).get('pa', [None])[0] if parsed.scheme == 'upi' else None
        if parsed.scheme == 'upi':
            if not payee:
                concerns.append('Payment URI lacks a payee identifier.')
        elif parsed.scheme not in ('https', 'http'):
            concerns.append('Unsupported destination scheme; inspect manually.')
        if parsed.username or parsed.password:
            concerns.append('URL contains embedded credentials or a misleading authority prefix.')
        if host in SHORTENERS:
            concerns.append('Shortened destination conceals the final domain.')
        if 'xn--' in host or any(ord(c) > 127 for c in host):
            concerns.append('Internationalized domain; check for visual lookalikes.')
        try:
            ipaddress.ip_address(host)
            concerns.append('Destination uses a literal IP address.')
        except ValueError:
            pass
        if parsed.scheme == 'http':
            concerns.append('Destination uses unencrypted HTTP.')
        return Destination(value=value, domain=host or None, payment_identifier=payee,
                           page=page, bbox=bbox, confidence=confidence, concerns=concerns)
    except ValueError:
        return Destination(value=value, page=page, bbox=bbox, confidence=confidence,
                           concerns=['Malformed destination; inspect manually.'])


def identities(fields, destinations):
    result = [Identity(type=f.type, value=f.value, page=f.page) for f in fields
              if f.type in {'entity', 'name', 'email', 'upi', 'account', 'registration', 'reference', 'phone'}]
    domains = {d.domain for d in destinations if d.domain and not d.payment_identifier}
    for item in result:
        if item.type == 'email':
            domain = item.value.rsplit('@', 1)[-1].lower()
            if domains and not any(domain == d or domain.endswith('.'+d) or d.endswith('.'+domain) for d in domains):
                item.inconsistencies.append('Contact email domain differs from listed website domains; affiliation is unverified.')
        if item.type == 'upi':
            payees = {d.payment_identifier.casefold() for d in destinations if d.payment_identifier}
            if payees and item.value.casefold() not in payees:
                item.inconsistencies.append('Printed UPI identifier differs from the decoded QR payment identifier.')
    # Names alone cannot establish domain ownership or payment-account ownership.
    return result
