"""The features the web subset keeps, read from web_features.txt, for the verify scripts.

The Makefile runs each verify script on the web subset with TS_WEB_SUBSET=1. There,
kept(tag) is False for a feature the subset drops, so the script skips that check;
on the full font every feature is kept and every check runs.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, 'web_features.txt')) as fh:
    WEB_FEATURES = frozenset(l.split('#')[0].strip() for l in fh if l.split('#')[0].strip())
SUBSET = os.environ.get('TS_WEB_SUBSET') == '1'


def kept(*tags):
    """True if every tag survives in the font under test (always, for the full font)."""
    return not SUBSET or all(t in WEB_FEATURES for t in tags)
