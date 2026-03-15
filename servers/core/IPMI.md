# ipmi commands

- sudo ipmitool sensor list
- 

## show bios

### settings
Advanced → Boot Feature → Quiet Boot → Disabled
Advanced → Serial Port Console Redirection → Console Redirection → Enabled
Advanced → Serial Port Console Redirection → Terminal Type → VT100+
Advanced → Serial Port Console Redirection → Out-of-Band Mgmt Port → COM1

output training data:
Advanced → AMD CBS → UMC Common Options → DDR4 Common Options → Memory Interleaving → (leave as-is, but look around this menu for):
Look for any of these options:

ABL Console Out → Enable (if it exists — this prints AGESA memory training logs to serial)
ABL Serial Port → SOL or BMC or COM1
Memory Training Verbose → Enable


#### output
After enabling and rebooting, SOL output during POST code 16 should show lines like:
ABL: Memory Training Start
ABL: DIMM 0: SPD Speed 2400 MT/s
ABL: Training Speed: 2400 MT/s
ABL: Channel 0: Write Leveling... PASS
ABL: Channel 0: Read DQS Training... PASS
ABL: Channel 0: Data Buffer Training... FAIL  ← this is where LRDIMMs die

### command
- ipmitool -I lanplus -H 192.168.10.226 -U ADMIN -P ADMIN sol activate