# Azure SKU Availability Checker

## Overview
This PowerShell script checks the availability of specific Azure VM sizes and disk types across selected Azure regions for your Pure Storage Cloud Block Store instance.

## Requirements
- PowerShell
- Azure PowerShell module (`Az`)
- Logged in via `Connect-AzAccount`

## Usage

`.\Check-SKU-Availability.ps1`

## Configuration

Modify these values as needed:- primarily `$regions`

```
$vmSizesR1 = @("Standard_D64s_v3", "Standard_D32s_v3")
$vmSizesR2 = @("Standard_E32bds_v5", "Standard_E16bds_v5")
$diskTypesR1 = @("UltraSSD_LRS")
$diskTypesR2 = @("PremiumV2_LRS")
$regions = @("centralindia", "southindia", "westindia", "jioindiacentral", "jioindiawest")
```

## Example Output
```
### Checking SKU Availability in southindia ...
Standard_D64s_v3 is supported in southindia region in the following zones:
Standard_D32s_v3 is supported in southindia region in the following zones:
Standard_E32bds_v5 is supported in southindia region in the following zones:
Standard_E16bds_v5 is supported in southindia region in the following zones:
UltraSSD_LRS is NOT supported in southindia region
PremiumV2_LRS is NOT supported in southindia region

in southindia
CBS v10R1 and v20R1 is NOT supported due to missing storage
CBS v10R2 and v20R2 is NOT supported due to missing storage
```

## License
MIT License

## Contributions
Submit a pull request with improvements.
