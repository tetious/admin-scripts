## admin-scripts

A collection of handy adminy things of marginal usefulness.

- inject-archived-email.ts -> Simple node script intended to run under Lambda that takes an email ingested into S3 via SES and gives it a more useful name.
- nightly-aws-backup.py -> Super simple backup script for Lambda that takes snapshots of marked EC2 volumes each night. Add the tag "backup" to any volumes you wish backed up. 