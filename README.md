# What it does
This python script will read all `components` and related `subscribers` from `source_pages` and publish them to `target_page`

Due to spam policy in StatusPage, users will have to re-confirm their email/sms before receiving notifications.


## Notes
- Supports Component Groups (but only name, not description of groups)
- Supports SMS and Email subscribers (not webhook)
- Any subscriber who signed up to a page before it introduced components will be subscribed to *all* components for that page.

## Running

1) Verify `source_pages` and `target_page` in [migrate.py](migrate.py).
1) set API key in [migrate.py](migrate.py)
2) `python migrate.py`


## OOPs!
Included is a [delete.py](delete.py) which will purge all components from target page in case you goof the migration and want to start over.
