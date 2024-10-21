# Specify file path and delete previous validation file
$FileManaged = "C:\Software_Develop\Repositorios_Lenguaje\Python\Scripts\Proyecto Power Shell\Netskopemanaged.txt"
$FileUnmanaged = "C:\Software_Develop\Repositorios_Lenguaje\Python\Scripts\Proyecto Power Shell\UnmanagedDevice.txt"

# Step 1: Verify if there is any existing "Managed Device" validation file
if (Test-Path $FileManaged) {
    # Delete previous validation file
    Remove-Item -Path $FileManaged -Force
    #Write-Host "The validation file has been deleted succesfully."
} else {
    #Write-Host "The validation file does not exist in the specified path."
}

# Verify if there is any existing "Unmanaged Device" validation file
if (Test-Path $FileUnmanaged) {
    # Delete the file
    Remove-Item -Path $FileUnmanaged -Force
    #Write-Host "The validation file has been deleted succesfully."
} else {
    #Write-Host "The validation file does not exist in the specified path."
}

# Step 2: Check if Antivirus process is running in the windows machine
$antivirusProcessRunning = Get-Process | Where-Object { $_.ProcessName -eq "MpDefenderCoreService" }
if ($antivirusProcessRunning -ne "" ) {
    $AVcheck = $true
} else {
	$AVcheck = $false
}
# Get-WmiObject -Namespace "root\SecurityCenter2" -Class AntiVirusProduct | Select-Object DisplayName, PathToSignedProductExe, ProductState

# Step 3: Validate if corporate DNS server is being used.
$dnsServer = ipconfig /all | Select-String -Pattern 'DNS Servers.*: (.*)' | ForEach-Object { $_.Matches.Groups[1].Value }
if ($dnsServer -like "192.168.0.2" ) {
    $dnsServercheck = $true
} else {
	$dnsServercheck = $false
}


# Step 4: Check if there is any existing live RDP traffic via tcp port or process name
$rdpTraffic = Get-NetTCPConnection | Where-Object { $_.RemotePort -eq 3389 -or $_.LocalPort -eq 3389 } | Select-Object -First 1
$rdpProcesses = Get-Process | Where-Object { $_.ProcessName -in @("teamviewer", "anydesk", "mstsc","SSUService") }

if ($rdpTraffic.length -eq 0  -and $rdpProcesses.length -eq 0) {
    $rdpChecker = $true
} else {
	$rdpChecker = $false
}

# Step 5: Check if all Windows-Firewall profiles (Domain,Public,Private) are enabled in the windows machine.
$WindowsFW = netsh advfirewall show all | Select-String -Pattern 'disabled'

if ($WindowsFW.length -eq 0) {
    $WFWChecker = $true
} else {
	$WFWChecker = $false
}

#Final Step - Write Output Files
if ($AVcheck -eq "true" -and $dnsServercheck -eq "true" -and $rdpChecker -eq "true" -and $WFWChecker -eq "true" ) {
    Out-File -FilePath $FileManaged
} else {
	$concatString = "Antivirus Enabled = " + $AVcheck.tostring() + ", " + "DNS Server Complaint = " + $dnsServercheck.tostring() + ", " + "Remote Sessions Disabled = " + $rdpChecker.tostring() + ", " + "Windows Firewall Enabled = " + $WFWChecker.tostring() 
	$concatString | Out-File -FilePath $FileUnmanaged
}

##############################################################################
# Step 5: Check user groups
#$currentUserName = $env:USERNAME
#$currentGroups = Get-LocalGroup -Member $currentUserName | Select-Object -ExpandProperty Name
#if ($currentGroups -notcontains "Administrators" -and $currentGroups -notcontains "IT-group") {
#    $managedDevice = $true
#}
##############################################################################
