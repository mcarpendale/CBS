# GetSnapshot-Detailed

**Purpose**  
Calculate the actual storage consumption of EBS snapshots (FULL & INCR), optionally across multiple AWS accounts, based on the [AWS Knowledge Center approach](https://repost.aws/knowledge-center/ebs-calculate-snapshot-size) (using `list_snapshot_blocks` and `list_changed_blocks`).

**Credits**: Original script logic by [Parag Nagwekar](https://github.com/aws-samples/aws-ebs-snapshots-awsorganizations/tree/main)

## Behavior and Notes

- **If `--role` is NOT specified**:  
  - The script analyzes snapshots only in the current AWS account, or a single specified account if `--account` is provided.
- **If `--role` IS specified**:  
  - The script attempts to list all active AWS accounts in your AWS Organization (requires `organizations:ListAccounts` permission) and assumes the given role in each account.

- **For each snapshot**:
  - Determines if it’s **FULL** (first snapshot on a volume) or **INCR** (subsequent snapshots).
  - Calculates approximate storage usage (in KiB/GiB) via EBS direct APIs.
  - Includes **VolumeSize**, **StorageTier**, and relevant tags (`Owner`, `Team`, `instance_id`), plus a JSON field with all tags.
  - Snapshots missing a `VolumeId` are included with **Type = "N/A"** (no incremental chain) and zero block usage.

### Required and Optional Arguments

- **`--region`** (required): For example, `us-east-1`.
- **`--file`** (optional): If provided, saves CSV output to the given filename; otherwise prints to stdout.
- **`--role`** (optional): If provided, the script enumerates Org accounts using `list_accounts` and assumes this role in each account.
- **`--account`** (optional): If provided (without `--role`), the script analyzes only that account. Otherwise, it defaults to the current account.

## Usage Examples

1. **Single account (current), print to screen**:
   ```bash
   python3 ./GetSnapshot-Detailed.py --region ap-southeast-1
2. **Single account (current), save results to CSV**:
   ```bash
   python3 ./GetSnapshot-Detailed.py --region ap-southeast-1 --file snapshots.csv
3. **Specify a particular account (no Org enumeration), save to CSV:**:
   ```bash
   python3 ./GetSnapshot-Detailed.py --region ap-southeast-1 \
    --account 123456789012 --file single_acct_snapshots.csv
4. **Enumerate all AWS Org accounts using a cross-account role**:
   ```bash
   python3 ./GetSnapshot-Detailed.py --region ap-southeast-1 \
    --role MyCrossAccountRole --file org_snapshots.csv
