# VM Disk Capacity & Performance Report

A KQL query for Azure Monitor Logs that produces a per-drive, per-VM report of disk capacity and peak performance metrics — using data collected by [VM Insights](https://learn.microsoft.com/en-us/azure/azure-monitor/vm/vminsights-overview).

## What it does

The query correlates `InsightsMetrics` data to produce a single row per drive per VM showing:

- **Capacity** — disk size, used/free space, percent used
- **Peak Write snapshot** — the moment of highest write throughput, with all other metrics (read MB/s, read/write IOPS, read/write latency) captured at that same timestamp
- **Peak Read snapshot** — same idea, anchored to the moment of highest read throughput

The `PW_` and `PR_` column prefixes indicate which peak the correlated values belong to. Null values mean a metric sample didn't land at that exact timestamp.

Drives are classified as `OS`, `Temp`, or `Data` based on mount point and size. Ephemeral/system mounts (`/mnt`, `/mnt/resource`, `/snap/*`, `/boot`, `/sys/*`) are excluded automatically.

## Prerequisites

- **VM Insights** must be enabled on target VMs — this is where the `InsightsMetrics` table comes from
- **Log Analytics workspace(s)** receiving the VM Insights data
- Permissions to query the workspace(s) via Azure Monitor Logs

## How to run

1. In the Azure portal, navigate to **Monitor → Logs**
2. Switch the editor to **KQL mode** (drop-down in the query toolbar)
3. Paste the contents of [`vm-disk-performance-capacity.kql`](vm-disk-performance-capacity.kql)
<img width="2520" height="1597" alt="Screenshot 2026-03-23 at 3 42 51 pm" src="https://github.com/user-attachments/assets/b1cd45ef-060a-4b92-a556-b80b3208b7e0" />

4. **Set the scope** — click the kebab menu (⋯) on the query tab and select **Change scope**
   - To query across all subscriptions: select each subscription
   - To narrow results: filter **Resource types** to `Log Analytics workspace` and select only the relevant workspace(s)
5. Set the **Time range** (e.g. Last 24 hours) and click **Run**

## Exporting results

Click **Share → Export to CSV (all columns)** to download the full result set for offline analysis or import into a TCO model.

## Output columns

| Column | Description |
|--------|-------------|
| `SubscriptionId` | Azure subscription GUID |
| `ResourceGroup` | VM resource group |
| `Computer` | VM hostname |
| `Drive` | Mount point / drive letter |
| `DriveType` | `OS`, `Temp`, or `Data` |
| `DiskSizeGB` | Total disk capacity |
| `UsedSpaceGB` / `FreeSpaceGB` | Average used and free space over the time range |
| `PctUsed` | Percent used |
| `PeakWriteTime` | Timestamp of maximum write throughput |
| `MaxWriteMBps` | Peak write throughput (MB/s) |
| `PW_ReadMBps` | Read throughput at peak write time |
| `PW_WriteIOPS` / `PW_ReadIOPS` | IOPS at peak write time |
| `PW_WriteLatMs` / `PW_ReadLatMs` | Latency at peak write time |
| `PeakReadTime` | Timestamp of maximum read throughput |
| `MaxReadMBps` | Peak read throughput (MB/s) |
| `PR_WriteMBps` | Write throughput at peak read time |
| `PR_ReadIOPS` / `PR_WriteIOPS` | IOPS at peak read time |
| `PR_ReadLatMs` / `PR_WriteLatMs` | Latency at peak read time |

## Files

| File | Description |
|------|-------------|
| [`vm-disk-performance-capacity.kql`](vm-disk-performance-capacity.kql) | The KQL query — paste directly into Azure Monitor Logs |
