#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# Name:        GetSnapshot-Detailed.py
# Purpose:     Calculate the actual storage consumption of EBS snapshots (FULL & INCR),
#              optionally across multiple AWS accounts, based on the AWS Knowledge Center
#              approach (list_snapshot_blocks, list_changed_blocks).
# Author:      Mike Carpendale
# Created:     21/01/2025
# Credits:     Original script logic by Parag Nagwekar
#              (https://github.com/aws-samples/aws-ebs-snapshots-awsorganizations/tree/main)
#
# Behavior and Notes:
#   - If --role is NOT specified:
#       * The script analyzes snapshots only in the current AWS account,
#         or a single specific account if --account is provided.
#   - If --role IS specified:
#       * The script attempts to list all active AWS accounts in your
#         AWS Organization (requires 'organizations:ListAccounts' permission)
#         and assumes the given role in each account.
#   - For each snapshot:
#       * Determines if it’s FULL (first snapshot on a volume) or INCR (subsequent).
#       * Calculates approximate storage usage (in KiB/GiB) via EBS direct APIs.
#       * Includes VolumeSize, StorageTier, relevant tags (Owner, Team, instance_id),
#         and a JSON field with all tags.
#       * Snapshots missing a VolumeId are included as Type="N/A" (no incremental chain),
#         with 0 block usage by default.
#
#   - Required and optional arguments:
#       * --region (required): e.g., 'us-east-1'.
#       * --file (optional): If provided, saves CSV to that file; else prints to stdout.
#       * --role (optional): If provided, enumerates Org accounts and assumes this role.
#       * --account (optional): If provided (without --role), analyzes only that account;
#         otherwise defaults to the current account.
#
# Usage Examples:
#   1) Single account (current), print to screen:
#       python3 ./GetSnapshot-Detailed.py --region ap-southeast-1
#
#   2) Single account (current), save results to CSV:
#       python3 ./GetSnapshot-Detailed.py --region ap-southeast-1 --file snapshots.csv
#
#   3) Specify a particular account (no Org enumeration), save to CSV:
#       python3 ./GetSnapshot-Detailed.py --region ap-southeast-1 \
#           --account 123456789012 --file single_acct_snapshots.csv
#
#   4) Enumerate all AWS Org accounts using a cross-account role:
#       python3 ./GetSnapshot-Detailed.py --region ap-southeast-1 \
#           --role MyCrossAccountRole --file org_snapshots.csv
#
#-------------------------------------------------------------------------------

import boto3
import argparse
import csv
import sys
import logging
import datetime
import os
import json

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)

# CSV columns we will produce:
FIELD_NAMES = [
    'Account',
    'SnapshotId',
    'VolumeId',
    'VolumeSize',    # In GiB as reported by AWS
    'StorageTier',   # Typically "standard" or "archive"
    'SnapshotTime',
    'Type',          # 'FULL', 'INCR', or 'N/A'
    'SizeKiB',
    'SizeGiB',
    'Owner',
    'Team',
    'instance_id',
    'Description',
    'TagsAll'
]

def get_all_org_accounts():
    """
    Return a list of all ACTIVE AWS account IDs in the Organization.
    Must be called from the Org management (payer) account or
    a delegated admin account with the right permissions (organizations:ListAccounts).
    """
    org_client = boto3.client('organizations')
    paginator = org_client.get_paginator('list_accounts')
    all_accts = []
    for page in paginator.paginate():
        for acct in page['Accounts']:
            if acct['Status'] == 'ACTIVE':
                all_accts.append(acct['Id'])
    return all_accts


def assume_role(account_id, role_name):
    """
    Assume the given role in the target account and return temporary credentials
    or None if the assume fails.
    """
    sts = boto3.client('sts')
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
    try:
        resp = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName='CrossAccountSession'
        )
        creds = resp['Credentials']
        return {
            'aws_access_key_id': creds['AccessKeyId'],
            'aws_secret_access_key': creds['SecretAccessKey'],
            'aws_session_token': creds['SessionToken'],
        }
    except ClientError as e:
        logging.error("Error assuming role in account %s: %s", account_id, str(e))
        return None


def describe_all_snapshots(ec2_client, account_id):
    """
    Return a combined list of all snapshots owned by the specified account_id.
    Uses pagination to retrieve up to 500 at a time.
    """
    snapshots = []
    params = {'OwnerIds': [account_id], 'MaxResults': 500}
    while True:
        resp = ec2_client.describe_snapshots(**params)
        snapshots.extend(resp['Snapshots'])
        if 'NextToken' not in resp:
            break
        params['NextToken'] = resp['NextToken']
    return snapshots


def list_snapshot_blocks(ebs_client, snapshot_id):
    """
    Return the total number of blocks in the given snapshot.
    Each block is 512 KiB. We'll multiply later to get KiB.
    """
    highest_block_index = 0
    next_token = None

    while True:
        if next_token:
            resp = ebs_client.list_snapshot_blocks(
                SnapshotId=snapshot_id,
                NextToken=next_token
            )
        else:
            resp = ebs_client.list_snapshot_blocks(SnapshotId=snapshot_id)

        blocks = resp.get('Blocks', [])
        for block in blocks:
            if block['BlockIndex'] > highest_block_index:
                highest_block_index = block['BlockIndex']

        next_token = resp.get('NextToken')
        if not next_token:
            break

    return highest_block_index + 1


def list_changed_blocks(ebs_client, first_snap, second_snap):
    """
    Return how many blocks changed between two snapshots.
    Each changed block is 512 KiB.
    """
    total_changed = 0
    next_token = None

    while True:
        if next_token:
            resp = ebs_client.list_changed_blocks(
                FirstSnapshotId=first_snap,
                SecondSnapshotId=second_snap,
                NextToken=next_token
            )
        else:
            resp = ebs_client.list_changed_blocks(
                FirstSnapshotId=first_snap,
                SecondSnapshotId=second_snap
            )

        changed_blocks = resp.get('ChangedBlocks', [])
        total_changed += len(changed_blocks)

        next_token = resp.get('NextToken')
        if not next_token:
            break

    return total_changed


def main():
    parser = argparse.ArgumentParser(description='Block-level EBS snapshot usage across multiple (Org) accounts.')
    parser.add_argument('--region', required=True, help='AWS region, e.g. us-east-1')
    parser.add_argument('--file', required=False, help='Output CSV file (otherwise prints to stdout in CSV).')
    parser.add_argument('--role', required=False, help='IAM role to assume in other accounts. If provided, we gather all Org accounts.')
    parser.add_argument('--account', required=False, help='Single account to query (otherwise current or all Org).')
    args = parser.parse_args()

    region = args.region
    out_file = args.file
    role_name = args.role
    single_account = args.account

    # Determine current account:
    sts_client = boto3.client('sts')
    this_account = sts_client.get_caller_identity()["Account"]

    # ORIGINAL LOGIC REPLICATED:
    # if --role is provided, gather all Org accounts
    # otherwise, if no --role is given, just do the single account or current account
    if role_name:
        # If we pass --account in addition to --role, we typically ignore it in original script
        # But you could decide to combine logic. We'll mimic original: gather all Org accounts
        accounts = get_all_org_accounts()
    else:
        # No role => just the single account if specified, else current
        if single_account:
            accounts = [single_account]
        else:
            accounts = [this_account]

    results = []

    for acct in accounts:
        # If we provided --role, we assume that role for each account (and it's not the current)
        # In original script, we skip assume_role if act == current_account
        if role_name and acct != this_account:
            creds = assume_role(acct, role_name)
            if not creds:
                logging.warning("Skipping account %s (assume_role failed).", acct)
                continue
            ec2_client = boto3.client('ec2', region_name=region, **creds)
            ebs_client = boto3.client('ebs', region_name=region, **creds)
        else:
            # either no role or same account => use default creds
            ec2_client = boto3.client('ec2', region_name=region)
            ebs_client = boto3.client('ebs', region_name=region)

        # Describe all snapshots in this account
        snaps = describe_all_snapshots(ec2_client, acct)
        if not snaps:
            logging.info("No snapshots found in account %s", acct)
            continue

        # Separate snapshots that DO have a VolumeId vs. those that do NOT
        volume_map = {}
        no_volume_snaps = []

        for s in snaps:
            vol_id = s.get('VolumeId')

            # We'll extract VolumeSize and StorageTier here so we can use them later
            volume_size = s.get('VolumeSize', 'N/A')   # in GiB, usually an int
            storage_tier = s.get('StorageTier', 'N/A') # "standard" or "archive" (if present)

            # Store these back into the snapshot object for convenience
            s['_VolumeSize'] = volume_size
            s['_StorageTier'] = storage_tier

            if vol_id:
                # Group by VolumeId for FULL vs INCR logic
                volume_map.setdefault(vol_id, []).append(s)
            else:
                # No VolumeId -> handle separately
                no_volume_snaps.append(s)

        # --- PART A: Snapshots that have a VolumeId (i.e., can do FULL vs. INCR) ---
        for vol_id, snap_list in volume_map.items():
            # Sort by StartTime to walk them in chronological order
            snap_list.sort(key=lambda x: x['StartTime'])
            prev_snap_id = None

            for idx, snap_obj in enumerate(snap_list):
                snap_id = snap_obj['SnapshotId']
                snap_time = snap_obj['StartTime']
                snapshot_time_str = snap_time.strftime('%Y-%m-%d %H:%M:%S')

                volume_size = snap_obj.get('_VolumeSize', 'N/A')
                storage_tier = snap_obj.get('_StorageTier', 'N/A')

                # Gather tags as a dictionary
                tags_dict = {}
                for t in snap_obj.get('Tags', []):
                    tags_dict[t['Key']] = t['Value']

                # Common fields
                owner_val = tags_dict.get('Owner', '')
                team_val = tags_dict.get('Team', '')
                instance_val = tags_dict.get('instance_id', '')
                description_val = snap_obj.get('Description', '')

                # All tags as JSON string
                all_tags_str = json.dumps(tags_dict)

                if idx == 0:
                    # First snapshot for this volume -> FULL
                    try:
                        block_count = list_snapshot_blocks(ebs_client, snap_id)
                        size_kib = block_count * 512
                        size_gib = size_kib / 1048576.0
                        snap_type = 'FULL'
                    except ClientError as e:
                        logging.error("Error in list_snapshot_blocks for snapshot %s: %s", snap_id, e)
                        snap_type = 'FULL'  # fallback
                        size_kib = 0
                        size_gib = 0
                else:
                    # Subsequent -> INCR
                    try:
                        changed_count = list_changed_blocks(ebs_client, prev_snap_id, snap_id)
                        size_kib = changed_count * 512
                        size_gib = size_kib / 1048576.0
                        snap_type = 'INCR'
                    except ClientError as e:
                        logging.error("Error in list_changed_blocks for snapshots %s -> %s: %s",
                                      prev_snap_id, snap_id, e)
                        snap_type = 'INCR'
                        size_kib = 0
                        size_gib = 0

                prev_snap_id = snap_id

                # Build final row:
                row = {
                    'Account': acct,
                    'SnapshotId': snap_id,
                    'VolumeId': vol_id,
                    'VolumeSize': volume_size,
                    'StorageTier': storage_tier,
                    'SnapshotTime': snapshot_time_str,
                    'Type': snap_type,
                    'SizeKiB': size_kib,
                    'SizeGiB': round(size_gib, 3),
                    'Owner': owner_val,
                    'Team': team_val,
                    'instance_id': instance_val,
                    'Description': description_val,
                    'TagsAll': all_tags_str
                }
                results.append(row)

        # --- PART B: Snapshots that have NO VolumeId ---
        # We cannot do FULL/INCR block diff, so label Type=N/A with zero block usage by default.
        for snap_obj in no_volume_snaps:
            snap_id = snap_obj['SnapshotId']
            snap_time = snap_obj['StartTime']
            snapshot_time_str = snap_time.strftime('%Y-%m-%d %H:%M:%S')

            volume_size = snap_obj.get('_VolumeSize', 'N/A')
            storage_tier = snap_obj.get('_StorageTier', 'N/A')

            tags_dict = {}
            for t in snap_obj.get('Tags', []):
                tags_dict[t['Key']] = t['Value']

            owner_val = tags_dict.get('Owner', '')
            team_val = tags_dict.get('Team', '')
            instance_val = tags_dict.get('instance_id', '')
            description_val = snap_obj.get('Description', '')
            all_tags_str = json.dumps(tags_dict)

            # By default, set block usage to 0
            size_kib = 0
            size_gib = 0.0
            snap_type = 'N/A'

            row = {
                'Account': acct,
                'SnapshotId': snap_id,
                'VolumeId': 'N/A',
                'VolumeSize': volume_size,
                'StorageTier': storage_tier,
                'SnapshotTime': snapshot_time_str,
                'Type': snap_type,
                'SizeKiB': size_kib,
                'SizeGiB': round(size_gib, 3),
                'Owner': owner_val,
                'Team': team_val,
                'instance_id': instance_val,
                'Description': description_val,
                'TagsAll': all_tags_str
            }
            results.append(row)

    # --- OUTPUT section ---
    if out_file:
        # Write to CSV file
        if os.path.exists(out_file):
            logging.error("File %s already exists. Not overwriting.", out_file)
            sys.exit(1)
        with open(out_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELD_NAMES)
            writer.writeheader()
            writer.writerows(results)
        print(f"Results written to {out_file}")
    else:
        # Print to stdout in CSV format
        writer = csv.DictWriter(sys.stdout, fieldnames=FIELD_NAMES)
        writer.writeheader()
        writer.writerows(results)


if __name__ == '__main__':
    main()
