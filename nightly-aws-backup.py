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
	
	to_tag = []
	
	for volume in volumes:
		vol_id = volume['VolumeId']
		snapshot_name = "%s-backup" % next(tag['Value'] for tag in volume['Tags'] if tag['Key'] == 'Name')
		print "Backing up volume %s with name %s." % (vol_id, snapshot_name)
		snap = ec.create_snapshot(VolumeId=vol_id, Description=snapshot_name)
		to_tag.append(snap['SnapshotId'])
	
	delete_date = datetime.date.today() + datetime.timedelta(days=RETENTION_DAYS)
	ec.create_tags(Resources=to_tag, Tags=[{'Key': 'DeleteOn', 'Value': delete_date.strftime('%Y-%m-%d')}])
	
	delete_on = datetime.date.today().strftime('%Y-%m-%d')
	delete_on_filters = [
		{'Name': 'tag-key', 'Values': ['DeleteOn']},
		{'Name': 'tag-value', 'Values': [delete_on]},
	]
	
	snapshots_to_delete = ec.describe_snapshots(OwnerIds=[str(ACCOUNT_ID)], Filters=delete_on_filters).get('Snapshots')
	
	print "Deleting %d expired snapshots!" % len(snapshots_to_delete)
	
	for snap in snapshots_to_delete:
		snap_id = snap['SnapshotId']
		print "Deleting snapshot %s." % snap_id
		ec.delete_snapshot(SnapshotId=snap_id)