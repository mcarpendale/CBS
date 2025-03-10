# AVS - Azure Resource Graph Explorer Query

## 📌 Overview
This query is used in **Azure Resource Graph Explorer** to collect details of **Azure VMware Solution (AVS) deployments**. The output provides key AVS configuration details, including cluster size, host information, SKU (AV36, AV36P, etc.), and availability zone.

The results from this query help assess AVS deployments across subscriptions and can be downloaded as a CSV for further analysis.

![Screenshot 2025-03-10 at 1 11 26 pm](https://github.com/user-attachments/assets/fbcf7505-6d17-4bf2-9007-aa67dfef45fe)


## 📊 Query Details
This query retrieves:
- **Subscription ID & Resource Group**: Identifies the AVS deployment.
- **AVS Cluster Details**: Includes cluster name, cluster ID, and number of hosts.
- **Host Information**: Lists all ESXi hosts in the cluster.
- **AVS SKU**: Identifies the AVS host type (e.g., AV36, AV36P, AV64).
- **Availability Zone**: Indicates where the AVS deployment resides.


