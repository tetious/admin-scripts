# Super simple nightly backup script for lambda.
# To use, plug in your account id, and adjust retention in days as appropriate.
#
# This is free and unencumbered software released into the public domain.

import boto3, datetime

RETENTION_DAYS = 14
ACCOUNT_ID = 0 # set this to your AWS account id

ec = boto3.client('ec2')

def lambda_handler(event, context):
	volumes = ec.describe_volumes(Filters=[{'Name': 'tag-key', 'Values': ['backup']}]).get('Volumes')

	print "Backing up %d volumes!" % len(volumes)

	for volume in volumes:
		vol_id = volume['VolumeId']
		snapshot_name = "%s-autobackup" % next(tag['Value'] for tag in volume['Tags'] if tag['Key'] == 'Name')
		print "Backing up volume %s with name %s." % (vol_id, snapshot_name)
		ec.create_snapshot(VolumeId=vol_id, Description=snapshot_name)

	snapshots = ec.describe_snapshots(OwnerIds=[str(ACCOUNT_ID)]).get('Snapshots')
	snapshots_to_delete = [snap['SnapshotId'] for snap in snapshots if snap['Description'].endswith('backup') and
							(datetime.date.today() - snap['StartTime'].date()).days > RETENTION_DAYS]

	print "Deleting %d expired snapshots!" % len(snapshots_to_delete)

	for snap_id in snapshots_to_delete:
		print "Deleting snapshot %s." % snap_id
		ec.delete_snapshot(SnapshotId=snap_id)
