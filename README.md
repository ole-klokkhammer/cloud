# Tools
* https://github.com/CorentinTh/it-tools
* https://github.com/makeplane/plane
* https://github.com/dimonomid/nerdlog
* https://github.com/autokitteh/autokitteh

## dotnet installation multiple

* sudo dotnet-install --version 8.0.100 --install-dir /usr/share/dotnet
* dotnet --list-sdks
* dotnet new globaljson --sdk-version 8.0.100
* dotnet --version

# 

zpool status db
  pool: db
 state: ONLINE
  scan: scrub repaired 0B in 00:00:04 with 0 errors on Sun Jul 12 00:24:05 2026
config:

	NAME                                           STATE     READ WRITE CKSUM
	db                                             ONLINE       0     0     0
	  mirror-0                                     ONLINE       0     0     0
	    nvme-eui.e8238fa6bf530001001b448b42d4e212  ONLINE       0     0     0
	    nvme-eui.e8238fa6bf530001001b448b481b2dab  ONLINE       0     0     0

zpool status ssd
  pool: ssd
 state: ONLINE
  scan: scrub repaired 0B in 00:02:49 with 0 errors on Sun Jul 12 00:26:53 2026
config:

	NAME                                         STATE     READ WRITE CKSUM
	ssd                                          ONLINE       0     0     0
	  nvme-eui.e8238fa6bf530001001b444a463cb32e  ONLINE       0     0     0
	  nvme-eui.e8238fa6bf530001001b444a463cb58b  ONLINE       0     0     0

zpool status hdd
  pool: hdd
 state: ONLINE
  scan: scrub repaired 0B in 09:10:28 with 0 errors on Sun Jul 12 09:34:30 2026
config:

	NAME                        STATE     READ WRITE CKSUM
	hdd                         ONLINE       0     0     0
	  mirror-0                  ONLINE       0     0     0
	    wwn-0x5000c500facd8b05  ONLINE       0     0     0
	    wwn-0x5000c500facd6e04  ONLINE       0     0     0
	  mirror-1                  ONLINE       0     0     0
	    wwn-0x5000c500db8adff8  ONLINE       0     0     0
	    wwn-0x5000c500fb9355e5  ONLINE       0     0     0

zpool detach db nvme-eui.e8238fa6bf530001001b448b481b2dab
zpool detach hdd wwn-0x5000c500fb9355e5
zpool attach ssd nvme-eui.e8238fa6bf530001001b444a463cb32e nvme-eui.e8238fa6bf530001001b448b481b2dab