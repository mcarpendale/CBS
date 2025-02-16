# Define the VM sizes and disk types to check
$vmSizesR1 = @("Standard_D64s_v3", "Standard_D32s_v3")
$vmSizesR2 = @("Standard_E32bds_v5", "Standard_E16bds_v5")
$diskTypesR1 = @("UltraSSD_LRS")
$diskTypesR2 = @("PremiumV2_LRS")

# List of specific Azure regions
$regions = @("centralindia", "southindia", "westindia", "jioindiacentral", "jioindiawest")

foreach ($region in $regions) {
    Write-Output "`n### Checking SKU Availability in $region ..."

    # Fetch available SKUs once per region
    $availableSkus = Get-AzComputeResourceSku | Where-Object { $_.Locations -contains $region }

    # Initialize support status
    $R1_VMs_Supported = $false
    $R2_VMs_Supported = $false
    $R1_Storage_Supported = $false
    $R2_Storage_Supported = $false

    # Check VM SKUs for R1
    foreach ($vmSize in $vmSizesR1) {
        $vmsku = $availableSkus | Where-Object { $_.Name -eq $vmSize -and $_.ResourceType -eq "virtualMachines" }
        if ($vmsku) {
            Write-Host "$vmSize is supported in $region region in the following zones: $($vmsku.LocationInfo[0].Zones -join ', ')" -ForegroundColor Green
            $R1_VMs_Supported = $true
        } else {
            Write-Host "$vmSize is NOT supported in $region region" -ForegroundColor Red
        }
    }

    # Check VM SKUs for R2
    foreach ($vmSize in $vmSizesR2) {
        $vmsku = $availableSkus | Where-Object { $_.Name -eq $vmSize -and $_.ResourceType -eq "virtualMachines" }
        if ($vmsku) {
            Write-Host "$vmSize is supported in $region region in the following zones: $($vmsku.LocationInfo[0].Zones -join ', ')" -ForegroundColor Green
            $R2_VMs_Supported = $true
        } else {
            Write-Host "$vmSize is NOT supported in $region region" -ForegroundColor Red
        }
    }

    # Check Storage SKUs for R1
    foreach ($diskType in $diskTypesR1) {
        $disksku = $availableSkus | Where-Object { $_.Name -eq $diskType -and $_.ResourceType -eq "disks" }
        if ($disksku) {
            Write-Host "$diskType is supported in $region region in the following zones: $($disksku.LocationInfo[0].Zones -join ', ')" -ForegroundColor Green
            $R1_Storage_Supported = $true
        } else {
            Write-Host "$diskType is NOT supported in $region region" -ForegroundColor Red
        }
    }

    # Check Storage SKUs for R2
    foreach ($diskType in $diskTypesR2) {
        $disksku = $availableSkus | Where-Object { $_.Name -eq $diskType -and $_.ResourceType -eq "disks" }
        if ($disksku) {
            Write-Host "$diskType is supported in $region region in the following zones: $($disksku.LocationInfo[0].Zones -join ', ')" -ForegroundColor Green
            $R2_Storage_Supported = $true
        } else {
            Write-Host "$diskType is NOT supported in $region region" -ForegroundColor Red
        }
    }

    # Final Summary
    Write-Output "`nin $region"
    if ($R1_VMs_Supported -and $R1_Storage_Supported) {
        Write-Output "CBS v10R1 and v20R1 is SUPPORTED"
    } elseif ($R1_VMs_Supported -and -not $R1_Storage_Supported) {
        Write-Output "CBS v10R1 and v20R1 is NOT supported due to missing storage"
    } elseif (-not $R1_VMs_Supported -and $R1_Storage_Supported) {
        Write-Output "CBS v10R1 and v20R1 is NOT supported due to missing compute"
    } else {
        Write-Output "CBS v10R1 and v20R1 is NOT supported due to missing compute and storage"
    }

    if ($R2_VMs_Supported -and $R2_Storage_Supported) {
        Write-Output "CBS v10R2 and v20R2 is SUPPORTED"
    } elseif ($R2_VMs_Supported -and -not $R2_Storage_Supported) {
        Write-Output "CBS v10R2 and v20R2 is NOT supported due to missing storage"
    } elseif (-not $R2_VMs_Supported -and $R2_Storage_Supported) {
        Write-Output "CBS v10R2 and v20R2 is NOT supported due to missing compute"
    } else {
        Write-Output "CBS v10R2 and v20R2 is NOT supported due to missing compute and storage"
    }
}
