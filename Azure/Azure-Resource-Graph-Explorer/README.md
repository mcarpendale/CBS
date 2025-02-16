# Azure Resource Graph Explorer Code

This code used in Azure Resource Graph Explorer to collect VM Disk information when considering if Pure Storage Cloud Block Store (CBS) could be an alternate option for data disks

`where osDisk = null` is a data disk that could be migrated to CBS

Download as a CVS after the query has executed

![image](https://github.com/user-attachments/assets/713eaf2b-eb64-46fa-9344-17facedc350d)

## Versions
[Version 1](https://github.com/mcarpendale/CBS/blob/main/Azure/Azure-Resource-Graph-Explorer/AzureResourceGraphExplorer_code) - Documented above

[Version 2](https://github.com/mcarpendale/CBS/blob/main/Azure/Azure-Resource-Graph-Explorer/AzureResourceGraphExplorer_code_v2) - in addition to v1, collects VM name, vNIC, and vNet association
