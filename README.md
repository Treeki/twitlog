a very simple Twitter stream event logger by [@_Ninji](https://twitter.com/_Ninji)

Compatible with Python 2 or 3, requires the 'twitter' package (`pip install twitter`)

This package currently includes two scripts:

- **logger.py**: saves all Twitter stream events to files (tagged per-day)
- **parser.py**: processes previously-logged stream data and compiles activity statistics into a SQLite database

These two components are kept separate so that statistics parsing can easily be modified (for new features, format changes, or whatever) without disturbing the Twitter connection, and with the ability to add new stats using retroactive data.

Both are configured using a single JSON file. Multiple instances can be run concurrently (e.g. for multiple accounts) by passing one JSON file to each.

# TODO

- automatic stream reconnection
- automatic compression of old logs
- more analytics?
- scripts to generate graphs and stuff from the database stats


