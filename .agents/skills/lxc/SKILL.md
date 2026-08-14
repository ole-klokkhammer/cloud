
man7.org > Linux > man-pages

Linux/UNIX system programming training

lxc.container.conf(5) — Linux manual page
NAME | DESCRIPTION | EXAMPLES | SEE ALSO | SEE ALSO | COLOPHON


 
lxc.container.conf(5)                               lxc.container.conf(5)
NAME         top
       lxc.container.conf - LXC container configuration file
DESCRIPTION         top
       LXC is the well-known and heavily tested low-level Linux container
       runtime. It is in active development since 2008 and has proven
       itself in critical production environments world-wide. Some of its
       core contributors are the same people that helped to implement
       various well-known containerization features inside the Linux
       kernel.

       LXC's main focus is system containers. That is, containers which
       offer an environment as close as possible as the one you'd get
       from a VM but without the overhead that comes with running a
       separate kernel and simulating all the hardware.

       This is achieved through a combination of kernel security features
       such as namespaces, mandatory access control and control groups.

       LXC has support for unprivileged containers. Unprivileged
       containers are containers that are run without any privilege. This
       requires support for user namespaces in the kernel that the
       container is run on. LXC was the first runtime to support
       unprivileged containers after user namespaces were merged into the
       mainline kernel.

       In essence, user namespaces isolate given sets of UIDs and GIDs.
       This is achieved by establishing a mapping between a range of UIDs
       and GIDs on the host to a different (unprivileged) range of UIDs
       and GIDs in the container. The kernel will translate this mapping
       in such a way that inside the container all UIDs and GIDs appear
       as you would expect from the host whereas on the host these UIDs
       and GIDs are in fact unprivileged. For example, a process running
       as UID and GID 0 inside the container might appear as UID and GID
       100000 on the host. The implementation and working details can be
       gathered from the corresponding user namespace man page.  UID and
       GID mappings can be defined with the lxc.idmap key.

       Linux containers are defined with a simple configuration file.
       Each option in the configuration file has the form key = value
       fitting in one line. The "#" character means the line is a
       comment. List options, like capabilities and cgroups options, can
       be used with no value to clear any previously defined values of
       that option.

       LXC namespaces configuration keys use single dots. This means
       complex configuration keys such as lxc.net.0 expose various
       subkeys such as lxc.net.0.type, lxc.net.0.link,
       lxc.net.0.ipv6.address, and others for even more fine-grained
       configuration.

   CONFIGURATION
       In order to ease administration of multiple related containers, it
       is possible to have a container configuration file cause another
       file to be loaded. For instance, network configuration can be
       defined in one common file which is included by multiple
       containers. Then, if the containers are moved to another host,
       only one file may need to be updated.

       lxc.include
              Specify the file to be included. The included file must be
              in the same valid lxc configuration file format.

   ARCHITECTURE
       Allows one to set the architecture for the container. For example,
       set a 32bits architecture for a container running 32bits binaries
       on a 64bits host. This fixes the container scripts which rely on
       the architecture to do some work like downloading the packages.

       lxc.arch
              Specify the architecture for the container.

              Some valid options are x86, i686, x86_64, amd64

   HOSTNAME
       The utsname section defines the hostname to be set for the
       container.  That means the container can set its own hostname
       without changing the one from the system. That makes the hostname
       private for the container.

       lxc.uts.name
              specify the hostname for the container

   HALT SIGNAL
       Allows one to specify signal name or number sent to the
       container's init process to cleanly shutdown the container.
       Different init systems could use different signals to perform
       clean shutdown sequence. This option allows the signal to be
       specified in kill(1) fashion, e.g.  SIGPWR, SIGRTMIN+14,
       SIGRTMAX-10 or plain number. The default signal is SIGPWR.

       lxc.signal.halt
              specify the signal used to halt the container

   REBOOT SIGNAL
       Allows one to specify signal name or number to reboot the
       container.  This option allows signal to be specified in kill(1)
       fashion, e.g.  SIGTERM, SIGRTMIN+14, SIGRTMAX-10 or plain number.
       The default signal is SIGINT.

       lxc.signal.reboot
              specify the signal used to reboot the container

   STOP SIGNAL
       Allows one to specify signal name or number to forcibly shutdown
       the container. This option allows signal to be specified in
       kill(1) fashion, e.g. SIGKILL, SIGRTMIN+14, SIGRTMAX-10 or plain
       number. The default signal is SIGKILL.

       lxc.signal.stop
              specify the signal used to stop the container

   INIT COMMAND
       Sets the command to use as the init system for the containers.

       lxc.execute.cmd
              Absolute path from container rootfs to the binary to run by
              default. This mostly makes sense for lxc-execute.

       lxc.init.cmd
              Absolute path from container rootfs to the binary to use as
              init. This mostly makes sense for lxc-start. Default is
              /sbin/init.

   INIT WORKING DIRECTORY
       Sets the absolute path inside the container as the working
       directory for the containers.  LXC will switch to this directory
       before executing init.

       lxc.init.cwd
              Absolute path inside the container to use as the working
              directory.

   INIT ID
       Sets the UID/GID to use for the init system, and subsequent
       commands.  Note that using a non-root UID when booting a system
       container will likely not work due to missing privileges. Setting
       the UID/GID is mostly useful when running application containers.
       Defaults to: UID(0), GID(0)

       lxc.init.uid
              UID to use for init.

       lxc.init.gid
              GID to use for init.

   CORE SCHEDULING
       Core scheduling defines if the container payload is marked as
       being schedulable on the same core. Doing so will cause the kernel
       scheduler to ensure that tasks that are not in the same group
       never run simultaneously on a core. This can serve as an extra
       security measure to prevent the container payload from using cross
       hyper thread attacks.

       lxc.sched.core
              The only allowed values are 0 and 1. Set this to 1 to
              create a core scheduling domain for the container or 0 to
              not create one.  If not set explicitly no core scheduling
              domain will be created for the container.

   PROC
       Configure proc filesystem for the container.

       lxc.proc.[proc file name]
              Specify the proc file name to be set. The file names
              available are those listed under /proc/PID/.  Example:

                            lxc.proc.oom_score_adj = 10

   EPHEMERAL
       Allows one to specify whether a container will be destroyed on
       shutdown.

       lxc.ephemeral
              The only allowed values are 0 and 1. Set this to 1 to
              destroy a container on shutdown.

   NETWORK
       The network section defines how the network is virtualized in the
       container. The network virtualization acts at layer two. In order
       to use the network virtualization, parameters must be specified to
       define the network interfaces of the container. Several virtual
       interfaces can be assigned and used in a container even if the
       system has only one physical network interface.

       lxc.net
              may be used without a value to clear all previous network
              options.

       lxc.net.[i].type
              specify what kind of network virtualization to be used for
              the container.  Must be specified before any other
              option(s) on the net device.  Multiple networks can be
              specified by using an additional index i after all
              lxc.net.* keys. For example, lxc.net.0.type = veth and
              lxc.net.1.type = veth specify two different networks of the
              same type. All keys sharing the same index i will be
              treated as belonging to the same network. For example,
              lxc.net.0.link = br0 will belong to lxc.net.0.type.
              Currently, the different virtualization types can be:

              empty: will create only the loopback interface.

              veth: a virtual ethernet pair device is created with one
              side assigned to the container and the other side on the
              host.  lxc.net.[i].veth.mode specifies the mode the veth
              parent will use on the host.  The accepted modes are bridge
              and router.  The mode defaults to bridge if not specified.
              In bridge mode the host side is attached to a bridge
              specified by the lxc.net.[i].link option.  If the bridge
              link is not specified, then the veth pair device will be
              created but not attached to any bridge.  Otherwise, the
              bridge has to be created on the system before starting the
              container.  lxc won't handle any configuration outside of
              the container.  In router mode static routes are created on
              the host for the container's IP addresses pointing to the
              host side veth interface.  Additionally Proxy ARP and Proxy
              NDP entries are added on the host side veth interface for
              the gateway IPs defined in the container to allow the
              container to reach the host.  By default, lxc chooses a
              name for the network device belonging to the outside of the
              container, but if you wish to handle this name yourselves,
              you can tell lxc to set a specific name with the
              lxc.net.[i].veth.pair option (except for unprivileged
              containers where this option is ignored for security
              reasons).  Static routes can be added on the host pointing
              to the container using the lxc.net.[i].veth.ipv4.route and
              lxc.net.[i].veth.ipv6.route options.  Several lines specify
              several routes.  The route is in format x.y.z.t/m, eg.
              192.168.1.0/24.  In bridge mode untagged VLAN membership
              can be set with the lxc.net.[i].veth.vlan.id option. It
              accepts a special value of 'none' indicating that the
              container port should be removed from the bridge's default
              untagged VLAN.  The lxc.net.[i].veth.vlan.tagged.id option
              can be specified multiple times to set the container's
              bridge port membership to one or more tagged VLANs.

              vlan: a vlan interface is linked with the interface
              specified by the lxc.net.[i].link and assigned to the
              container. The vlan identifier is specified with the option
              lxc.net.[i].vlan.id.

              macvlan: a macvlan interface is linked with the interface
              specified by the lxc.net.[i].link and assigned to the
              container.  lxc.net.[i].macvlan.mode specifies the mode the
              macvlan will use to communicate between different macvlan
              on the same upper device. The accepted modes are private,
              vepa, bridge and passthru.  In private mode, the device
              never communicates with any other device on the same
              upper_dev (default).  In vepa mode, the new Virtual
              Ethernet Port Aggregator (VEPA) mode, it assumes that the
              adjacent bridge returns all frames where both source and
              destination are local to the macvlan port, i.e. the bridge
              is set up as a reflective relay. Broadcast frames coming in
              from the upper_dev get flooded to all macvlan interfaces in
              VEPA mode, local frames are not delivered locally. In
              bridge mode, it provides the behavior of a simple bridge
              between different macvlan interfaces on the same port.
              Frames from one interface to another one get delivered
              directly and are not sent out externally. Broadcast frames
              get flooded to all other bridge ports and to the external
              interface, but when they come back from a reflective relay,
              we don't deliver them again. Since we know all the MAC
              addresses, the macvlan bridge mode does not require
              learning or STP like the bridge module does. In passthru
              mode, all frames received by the physical interface are
              forwarded to the macvlan interface. Only one macvlan
              interface in passthru mode is possible for one physical
              interface.

              ipvlan: an ipvlan interface is linked with the interface
              specified by the lxc.net.[i].link and assigned to the
              container.  lxc.net.[i].ipvlan.mode specifies the mode the
              ipvlan will use to communicate between different ipvlan on
              the same upper device. The accepted modes are l3, l3s and
              l2. It defaults to l3 mode.  In l3 mode TX processing up to
              L3 happens on the stack instance attached to the dependent
              device and packets are switched to the stack instance of
              the parent device for the L2 processing and routing from
              that instance will be used before packets are queued on the
              outbound device. In this mode the dependent devices will
              not receive nor can send multicast / broadcast traffic.  In
              l3s mode TX processing is very similar to the L3 mode
              except that iptables (conn-tracking) works in this mode and
              hence it is L3-symmetric (L3s).  This will have slightly
              less performance but that shouldn't matter since you are
              choosing this mode over plain-L3 mode to make conn-tracking
              work.  In l2 mode TX processing happens on the stack
              instance attached to the dependent device and packets are
              switched and queued to the parent device to send devices
              out. In this mode the dependent devices will RX/TX
              multicast and broadcast (if applicable) as well.
              lxc.net.[i].ipvlan.isolation specifies the isolation mode.
              The accepted isolation values are bridge, private and vepa.
              It defaults to bridge.  In bridge isolation mode dependent
              devices can cross-talk among themselves apart from talking
              through the parent device.  In private isolation mode the
              port is set in private mode.  i.e. port won't allow cross
              communication between dependent devices.  In vepa isolation
              mode the port is set in VEPA mode.  i.e. port will offload
              switching functionality to the external entity as described
              in 802.1Qbg.

              phys: an already existing interface specified by the
              lxc.net.[i].link is assigned to the container.

       lxc.net.[i].flags
              Specify an action to do for the network.

              up: activates the interface.

       lxc.net.[i].link
              Specify the interface to be used for real network traffic.

       lxc.net.[i].l2proxy
              Controls whether layer 2 IP neighbour proxy entries will be
              added to the lxc.net.[i].link interface for the IP
              addresses of the container.  Can be set to 0 or 1. Defaults
              to 0.  When used with IPv4 addresses, the following sysctl
              values need to be set: net.ipv4.conf.[link].forwarding=1
              When used with IPv6 addresses, the following sysctl values
              need to be set: net.ipv6.conf.[link].proxy_ndp=1
              net.ipv6.conf.[link].forwarding=1

       lxc.net.[i].mtu
              Specify the maximum transfer unit for this interface.

       lxc.net.[i].name
              The interface name is dynamically allocated, but if another
              name is needed because the configuration files being used
              by the container use a generic name, eg. eth0, this option
              will rename the interface in the container.

       lxc.net.[i].hwaddr
              The interface mac address is dynamically allocated by
              default to the virtual interface, but in some cases, this
              is needed to resolve a mac address conflict or to always
              have the same link-local ipv6 address. Any "x" in address
              will be replaced by random value, this allows setting
              hwaddr templates.

       lxc.net.[i].ipv4.address
              Specify the ipv4 address to assign to the virtualized
              interface.  Several lines specify several ipv4 addresses.
              The address is in format x.y.z.t/m, eg. 192.168.1.123/24.
              You can optionally specify the broadcast address after the
              IP address, e.g. 192.168.1.123/24 255.255.255.255.
              Otherwise it is automatically calculated from the IP
              address.

       lxc.net.[i].ipv4.gateway
              Specify the ipv4 address to use as the gateway inside the
              container. The address is in format x.y.z.t, eg.
              192.168.1.123.  Can also have the special value auto, which
              means to take the primary address from the bridge interface
              (as specified by the lxc.net.[i].link option) and use that
              as the gateway. auto is only available when using the veth,
              macvlan and ipvlan network types.  Can also have the
              special value of dev, which means to set the default
              gateway as a device route.  This is primarily for use with
              layer 3 network modes, such as IPVLAN.

       lxc.net.[i].ipv6.address
              Specify the ipv6 address to assign to the virtualized
              interface. Several lines specify several ipv6 addresses.
              The address is in format x::y/m, eg.
              2003:db8:1:0:214:1234:fe0b:3596/64

       lxc.net.[i].ipv6.gateway
              Specify the ipv6 address to use as the gateway inside the
              container. The address is in format x::y, eg.
              2003:db8:1:0::1 Can also have the special value auto, which
              means to take the primary address from the bridge interface
              (as specified by the lxc.net.[i].link option) and use that
              as the gateway. auto is only available when using the veth,
              macvlan and ipvlan network types.  Can also have the
              special value of dev, which means to set the default
              gateway as a device route.  This is primarily for use with
              layer 3 network modes, such as IPVLAN.

       lxc.net.[i].script.up
              Add a configuration option to specify a script to be
              executed after creating and configuring the network used
              from the host side.

              In addition to the information available to all hooks. The
              following information is provided to the script:

              • LXC_HOOK_TYPE: the hook type. This is either 'up' or
                'down'.

              • LXC_HOOK_SECTION: the section type 'net'.

              • LXC_NET_TYPE: the network type. This is one of the valid
                network types listed here (e.g. 'vlan', 'macvlan',
                'ipvlan', 'veth').

              • LXC_NET_PARENT: the parent device on the host. This is
                only set for network types 'mavclan', 'veth', 'phys'.

              • LXC_NET_PEER: the name of the peer device on the host.
                This is only set for 'veth' network types. Note that this
                information is only available when lxc.hook.version is
                set to 1.

       Whether this information is provided in the form of environment
       variables or as arguments to the script depends on the value of
       lxc.hook.version. If set to 1 then information is provided in the
       form of environment variables. If set to 0 information is provided
       as arguments to the script.

       Standard output from the script is logged at debug level.
       Standard error is not logged, but can be captured by the hook
       redirecting its standard error to standard output.

       lxc.net.[i].script.down
              Add a configuration option to specify a script to be
              executed before destroying the network used from the host
              side.

              In addition to the information available to all hooks. The
              following information is provided to the script:

              • LXC_HOOK_TYPE: the hook type. This is either 'up' or
                'down'.

              • LXC_HOOK_SECTION: the section type 'net'.

              • LXC_NET_TYPE: the network type. This is one of the valid
                network types listed here (e.g. 'vlan', 'macvlan',
                'ipvlan', 'veth').

              • LXC_NET_PARENT: the parent device on the host. This is
                only set for network types 'mavclan', 'veth', 'phys'.

              • LXC_NET_PEER: the name of the peer device on the host.
                This is only set for 'veth' network types. Note that this
                information is only available when lxc.hook.version is
                set to 1.

       Whether this information is provided in the form of environment
       variables or as arguments to the script depends on the value of
       lxc.hook.version. If set to 1 then information is provided in the
       form of environment variables. If set to 0 information is provided
       as arguments to the script.

       Standard output from the script is logged at debug level.
       Standard error is not logged, but can be captured by the hook
       redirecting its standard error to standard output.

   NEW PSEUDO TTY INSTANCE (DEVPTS)
       For stricter isolation the container can have its own private
       instance of the pseudo tty.

       lxc.pty.max
              If set, the container will have a new pseudo tty instance,
              making this private to it. The value specifies the maximum
              number of pseudo ttys allowed for a pty instance (this
              limitation is not implemented yet).

   CONTAINER SYSTEM CONSOLE
       If the container is configured with a root filesystem and the
       inittab file is setup to use the console, you may want to specify
       where the output of this console goes.

       lxc.console.buffer.size
              Setting this option instructs liblxc to allocate an in-
              memory ringbuffer. The container's console output will be
              written to the ringbuffer. Note that ringbuffer must be at
              least as big as a standard page size. When passed a value
              smaller than a single page size liblxc will allocate a
              ringbuffer of a single page size. A page size is usually
              4KB.  The keyword 'auto' will cause liblxc to allocate a
              ringbuffer of 128KB.  When manually specifying a size for
              the ringbuffer the value should be a power of 2 when
              converted to bytes. Valid size prefixes are 'KB', 'MB',
              'GB'. (Note that all conversions are based on multiples of
              1024. That means 'KB' == 'KiB', 'MB' == 'MiB', 'GB' ==
              'GiB'.  Additionally, the case of the suffix is ignored,
              i.e. 'kB', 'KB' and 'Kb' are treated equally.)

       lxc.console.size
              Setting this option instructs liblxc to place a limit on
              the size of the console log file specified in
              lxc.console.logfile. Note that size of the log file must be
              at least as big as a standard page size. When passed a
              value smaller than a single page size liblxc will set the
              size of log file to a single page size. A page size is
              usually 4KB.  The keyword 'auto' will cause liblxc to place
              a limit of 128KB on the log file.  When manually specifying
              a size for the log file the value should be a power of 2
              when converted to bytes. Valid size prefixes are 'KB',
              'MB', 'GB'. (Note that all conversions are based on
              multiples of 1024. That means 'KB' == 'KiB', 'MB' == 'MiB',
              'GB' == 'GiB'.  Additionally, the case of the suffix is
              ignored, i.e. 'kB', 'KB' and 'Kb' are treated equally.)  If
              users want to mirror the console ringbuffer on disk they
              should set lxc.console.size equal to
              lxc.console.buffer.size.

       lxc.console.logfile
              Specify a path to a file where the console output will be
              written.  Note that in contrast to the on-disk ringbuffer
              logfile this file will keep growing potentially filling up
              the users disks if not rotated and deleted. This problem
              can also be avoided by using the in-memory ringbuffer
              option lxc.console.buffer.size.

       lxc.console.rotate
              Whether to rotate the console logfile specified in
              lxc.console.logfile. Users can send an API request to
              rotate the logfile. Note that the old logfile will have the
              same name as the original with the suffix ".1" appended.
              Users wishing to prevent the console log file from filling
              the disk should rotate the logfile and delete it if
              unneeded. This problem can also be avoided by using the in-
              memory ringbuffer option lxc.console.buffer.size.

       lxc.console.path
              Specify a path to a device to which the console will be
              attached. The keyword 'none' will simply disable the
              console. Note, when specifying 'none' and creating a device
              node for the console in the container at /dev/console or
              bind-mounting the hosts's /dev/console into the container
              at /dev/console the container will have direct access to
              the hosts's /dev/console.  This is dangerous when the
              container has write access to the device and should thus be
              used with caution.

   CONSOLE THROUGH THE TTYS
       This option is useful if the container is configured with a root
       filesystem and the inittab file is setup to launch a getty on the
       ttys. The option specifies the number of ttys to be available for
       the container. The number of gettys in the inittab file of the
       container should not be greater than the number of ttys specified
       in this option, otherwise the excess getty sessions will die and
       respawn indefinitely giving annoying messages on the console or in
       /var/log/messages.

       lxc.tty.max
              Specify the number of tty to make available to the
              container.

   CONSOLE DEVICES LOCATION
       LXC consoles are provided through Unix98 PTYs created on the host
       and bind-mounted over the expected devices in the container.  By
       default, they are bind-mounted over /dev/console and /dev/ttyN.
       This can prevent package upgrades in the guest. Therefore you can
       specify a directory location (under /dev under which LXC will
       create the files and bind-mount over them. These will then be
       symbolically linked to /dev/console and /dev/ttyN.  A package
       upgrade can then succeed as it is able to remove and replace the
       symbolic links.

       lxc.tty.dir
              Specify a directory under /dev under which to create the
              container console devices. Note that LXC will move any
              bind-mounts or device nodes for /dev/console into this
              directory.

   /DEV DIRECTORY
       By default, lxc creates a few symbolic links
       (fd,stdin,stdout,stderr) in the container's /dev directory but
       does not automatically create device node entries. This allows the
       container's /dev to be set up as needed in the container rootfs.
       If lxc.autodev is set to 1, then after mounting the container's
       rootfs LXC will mount a fresh tmpfs under /dev (limited to 500K by
       default, unless defined in lxc.autodev.tmpfs.size) and fill in a
       minimal set of initial devices.  This is generally required when
       starting a container containing a "systemd" based "init" but may
       be optional at other times. Additional devices in the containers
       /dev directory may be created through the use of the
       lxc.hook.autodev hook.

       lxc.autodev
              Set this to 0 to stop LXC from mounting and populating a
              minimal /dev when starting the container.

       lxc.autodev.tmpfs.size
              Set this to define the size of the /dev tmpfs.  The default
              value is 500000 (500K). If the parameter is used but
              without value, the default value is used.

   MOUNT POINTS
       The mount points section specifies the different places to be
       mounted. These mount points will be private to the container and
       won't be visible by the processes running outside of the
       container. This is useful to mount /etc, /var or /home for
       examples.

       NOTE - LXC will generally ensure that mount targets and relative
       bind-mount sources are properly confined under the container root,
       to avoid attacks involving over-mounting host directories and
       files. (Symbolic links in absolute mount sources are ignored)
       However, if the container configuration first mounts a directory
       which is under the control of the container user, such as
       /home/joe, into the container at some path, and then mounts under
       path, then a TOCTTOU attack would be possible where the container
       user modifies a symbolic link under their home directory at just
       the right time.

       lxc.mount.fstab
              specify a file location in the fstab format, containing the
              mount information. The mount target location can and in
              most cases should be a relative path, which will become
              relative to the mounted container root. For instance,

                           proc proc proc nodev,noexec,nosuid 0 0

              Will mount a proc filesystem under the container's /proc,
              regardless of where the root filesystem comes from. This is
              resilient to block device backed filesystems as well as
              container cloning.

              Note that when mounting a filesystem from an image file or
              block device the third field (fs_vfstype) cannot be auto as
              with mount(8) but must be explicitly specified.

       lxc.mount.entry
              Specify a mount point corresponding to a line in the fstab
              format.  Moreover lxc supports mount propagation, such as
              rshared or rprivate, and adds three additional mount
              options.  optional don't fail if mount does not work.
              create=dir or create=file to create dir (or file) when the
              point will be mounted.  relative source path is taken to be
              relative to the mounted container root. For instance,

                           dev/null proc/kcore none bind,relative 0 0

              Will expand dev/null to ${LXC_ROOTFS_MOUNT}/dev/null, and
              mount it to proc/kcore inside the container.

       lxc.mount.auto
              specify which standard kernel file systems should be
              automatically mounted. This may dramatically simplify the
              configuration. The file systems are:

              • proc:mixed (or proc): mount /proc as read-write, but
                remount /proc/sys and /proc/sysrq-trigger read-only for
                security / container isolation purposes.

              • proc:rw: mount /proc as read-write

              • sys:mixed (or sys): mount /sys as read-only but with
                /sys/devices/virtual/net writable.

              • sys:ro: mount /sys as read-only for security / container
                isolation purposes.

              • sys:rw: mount /sys as read-write

              • cgroup:mixed: Mount a tmpfs to /sys/fs/cgroup, create
                directories for all hierarchies to which the container is
                added, create subdirectories in those hierarchies with
                the name of the cgroup, and bind-mount the container's
                own cgroup into that directory. The container will be
                able to write to its own cgroup directory, but not the
                parents, since they will be remounted read-only.

              • cgroup:mixed:force: The force option will cause LXC to
                perform the cgroup mounts for the container under all
                circumstances.  Otherwise it is similar to cgroup:mixed.
                This is mainly useful when the cgroup namespaces are
                enabled where LXC will normally leave mounting cgroups to
                the init binary of the container since it is perfectly
                safe to do so.

              • cgroup:ro: similar to cgroup:mixed, but everything will
                be mounted read-only.

              • cgroup:ro:force: The force option will cause LXC to
                perform the cgroup mounts for the container under all
                circumstances.  Otherwise it is similar to cgroup:ro.
                This is mainly useful when the cgroup namespaces are
                enabled where LXC will normally leave mounting cgroups to
                the init binary of the container since it is perfectly
                safe to do so.

              • cgroup:rw: similar to cgroup:mixed, but everything will
                be mounted read-write. Note that the paths leading up to
                the container's own cgroup will be writable, but will not
                be a cgroup filesystem but just part of the tmpfs of
                /sys/fs/cgroup

              • cgroup:rw:force: The force option will cause LXC to
                perform the cgroup mounts for the container under all
                circumstances.  Otherwise it is similar to cgroup:rw.
                This is mainly useful when the cgroup namespaces are
                enabled where LXC will normally leave mounting cgroups to
                the init binary of the container since it is perfectly
                safe to do so.

              • cgroup (without specifier): defaults to cgroup:rw if the
                container retains the CAP_SYS_ADMIN capability,
                cgroup:mixed otherwise.

              • cgroup-full:mixed: mount a tmpfs to /sys/fs/cgroup,
                create directories for all hierarchies to which the
                container is added, bind-mount the hierarchies from the
                host to the container and make everything read-only
                except the container's own cgroup. Note that compared to
                cgroup, where all paths leading up to the container's own
                cgroup are just simple directories in the underlying
                tmpfs, here /sys/fs/cgroup/$hierarchy will contain the
                host's full cgroup hierarchy, albeit read-only outside
                the container's own cgroup.  This may leak quite a bit of
                information into the container.

              • cgroup-full:mixed:force: The force option will cause LXC
                to perform the cgroup mounts for the container under all
                circumstances.  Otherwise it is similar to
                cgroup-full:mixed.  This is mainly useful when the cgroup
                namespaces are enabled where LXC will normally leave
                mounting cgroups to the init binary of the container
                since it is perfectly safe to do so.

              • cgroup-full:ro: similar to cgroup-full:mixed, but
                everything will be mounted read-only.

              • cgroup-full:ro:force: The force option will cause LXC to
                perform the cgroup mounts for the container under all
                circumstances.  Otherwise it is similar to
                cgroup-full:ro.  This is mainly useful when the cgroup
                namespaces are enabled where LXC will normally leave
                mounting cgroups to the init binary of the container
                since it is perfectly safe to do so.

              • cgroup-full:rw: similar to cgroup-full:mixed, but
                everything will be mounted read-write. Note that in this
                case, the container may escape its own cgroup. (Note also
                that if the container has CAP_SYS_ADMIN support and can
                mount the cgroup filesystem itself, it may do so anyway.)

              • cgroup-full:rw:force: The force option will cause LXC to
                perform the cgroup mounts for the container under all
                circumstances.  Otherwise it is similar to
                cgroup-full:rw.  This is mainly useful when the cgroup
                namespaces are enabled where LXC will normally leave
                mounting cgroups to the init binary of the container
                since it is perfectly safe to do so.

              • cgroup-full (without specifier): defaults to
                cgroup-full:rw if the container retains the CAP_SYS_ADMIN
                capability, cgroup-full:mixed otherwise.

       If cgroup namespaces are enabled, then any cgroup auto-mounting
       request will be ignored, since the container can mount the
       filesystems itself, and automounting can confuse the container
       init.

       Note that if automatic mounting of the cgroup filesystem is
       enabled, the tmpfs under /sys/fs/cgroup will always be mounted
       read-write (but for the :mixed and :ro cases, the individual
       hierarchies, /sys/fs/cgroup/$hierarchy, will be read-only). This
       is in order to work around a quirk in Ubuntu's mountall(8) command
       that will cause containers to wait for user input at boot if
       /sys/fs/cgroup is mounted read-only and the container can't
       remount it read-write due to a lack of CAP_SYS_ADMIN.

       Examples:

                     lxc.mount.auto = proc sys cgroup
                     lxc.mount.auto = proc:rw sys:rw cgroup-full:rw

   ROOT FILE SYSTEM
       The root file system of the container can be different than that
       of the host system.

       lxc.rootfs.path
              specify the root file system for the container. It can be
              an image file, a directory or a block device. If not
              specified, the container shares its root file system with
              the host.

              For directory or simple block-device backed containers, a
              pathname can be used. If the rootfs is backed by a nbd
              device, then nbd:file:1 specifies that file should be
              attached to a nbd device, and partition 1 should be mounted
              as the rootfs.  nbd:file specifies that the nbd device
              itself should be mounted. overlayfs:/lower:/upper specifies
              that the rootfs should be an overlay with /upper being
              mounted read-write over a read-only mount of /lower.  For
              overlay multiple /lower directories can be specified.
              loop:/file tells lxc to attach /file to a loop device and
              mount the loop device.

       lxc.rootfs.mount
              where to recursively bind lxc.rootfs.path before pivoting.
              This is to ensure success of the pivot_root(8) syscall. Any
              directory suffices, the default should generally work.

       lxc.rootfs.options
              Specify extra mount options to use when mounting the
              rootfs.  The format of the mount options corresponds to the
              format used in fstab. In addition, LXC supports the custom
              idmap= mount option. This option can be used to tell LXC to
              create an idmapped mount for the container's rootfs. This
              is useful when the user doesn't want to recursively chown
              the rootfs of the container to match the idmapping of the
              user namespace the container is going to use. Instead an
              idmapped mount can be used to handle this.  The argument
              for idmap= can either be a path pointing to a user
              namespace file that LXC will open and use to idmap the
              rootfs or the special value "container" which will instruct
              LXC to use the container's user namespace to idmap the
              rootfs.

       lxc.rootfs.managed
              Set this to 0 to indicate that LXC is not managing the
              container storage, then LXC will not modify the container
              storage. The default is 1.

   CONTROL GROUPS ("CGROUPS")
       The control group section contains the configuration for the
       different subsystem. lxc does not check the correctness of the
       subsystem name. This has the disadvantage of not detecting
       configuration errors until the container is started, but has the
       advantage of permitting any future subsystem.

       The kernel implementation of cgroups has changed significantly
       over the years. With Linux 4.5 support for a new cgroup filesystem
       was added usually referred to as "cgroup2" or "unified hierarchy".
       Since then the old cgroup filesystem is usually referred to as
       "cgroup1" or the "legacy hierarchies". Please see the cgroups
       manual page for a detailed explanation of the differences between
       the two versions.

       LXC distinguishes settings for the legacy and the unified
       hierarchy by using different configuration key prefixes. To alter
       settings for controllers in a legacy hierarchy the key prefix
       lxc.cgroup. must be used and in order to alter the settings for a
       controller in the unified hierarchy the lxc.cgroup2. key must be
       used. Note that LXC will ignore lxc.cgroup. settings on systems
       that only use the unified hierarchy. Conversely, it will ignore
       lxc.cgroup2. options on systems that only use legacy hierarchies.
       lxc.cgroup. (legacy and hybrid hierarchy) support is dropped.

       At its core a cgroup hierarchy is a way to hierarchically organize
       processes. Usually a cgroup hierarchy will have one or more
       "controllers" enabled. A "controller" in a cgroup hierarchy is
       usually responsible for distributing a specific type of system
       resource along the hierarchy. Controllers include the "pids"
       controller, the "cpu" controller, the "memory" controller and
       others. Some controllers however do not fall into the category of
       distributing a system resource, instead they are often referred to
       as "utility" controllers.  One utility controller is the device
       controller. Instead of distributing a system resource it allows
       one to manage device access.

       In the legacy hierarchy the device controller was implemented like
       most other controllers as a set of files that could be written to.
       These files where named "devices.allow" and "devices.deny". The
       legacy device controller allowed the implementation of both
       "allowlists" and "denylists".

       An allowlist is a device program that by default blocks access to
       all devices. In order to access specific devices "allow rules" for
       particular devices or device classes must be specified. In
       contrast, a denylist is a device program that by default allows
       access to all devices. In order to restrict access to specific
       devices "deny rules" for particular devices or device classes must
       be specified.

       In the unified cgroup hierarchy the implementation of the device
       controller has completely changed. Instead of files to read from
       and write to a eBPF program of BPF_PROG_TYPE_CGROUP_DEVICE can be
       attached to a cgroup. Even though the kernel implementation has
       changed completely LXC tries to allow for the same semantics to be
       followed in the legacy device cgroup and the unified eBPF-based
       device controller. The following paragraphs explain the semantics
       for the unified eBPF-based device controller.

       As mentioned the format for specifying device rules for the
       unified eBPF-based device controller is the same as for the legacy
       cgroup device controller; only the configuration key prefix has
       changed.  Specifically, device rules for the legacy cgroup device
       controller are specified via lxc.cgroup.devices.allow and
       lxc.cgroup.devices.deny whereas for the cgroup2 eBPF-based device
       controller lxc.cgroup2.devices.allow and lxc.cgroup2.devices.deny
       must be used.

       • A denylist device rule

                      lxc.cgroup2.devices.deny = a

         will cause LXC to instruct the kernel to block access to all
         devices by default. To grant access to devices allow device
         rules must be added via the lxc.cgroup2.devices.allow key. This
         is referred to as a "allowlist" device program.

       • An allowlist device rule

                      lxc.cgroup2.devices.allow = a

         will cause LXC to instruct the kernel to allow access to all
         devices by default. To deny access to devices deny device rules
         must be added via lxc.cgroup2.devices.deny key.  This is
         referred to as a "denylist" device program.

       • Specifying any of the aforementioned two rules will cause all
         previous rules to be cleared, i.e. the device list will be
         reset.

       • When an allowlist program is requested, i.e. access to all
         devices is blocked by default, specific deny rules for
         individual devices or device classes are ignored.

       • When a denylist program is requested, i.e. access to all devices
         is allowed by default, specific allow rules for individual
         devices or device classes are ignored.

       For example the set of rules:

                 lxc.cgroup2.devices.deny = a
                 lxc.cgroup2.devices.allow = c *:* m
                 lxc.cgroup2.devices.allow = b *:* m
                 lxc.cgroup2.devices.allow = c 1:3 rwm

       implements an allowlist device program, i.e. the kernel will block
       access to all devices not specifically allowed in this list. This
       particular program states that all character and block devices may
       be created but only /dev/null might be read or written.

       If we instead switch to the following set of rules:

                 lxc.cgroup2.devices.allow = a
                 lxc.cgroup2.devices.deny = c *:* m
                 lxc.cgroup2.devices.deny = b *:* m
                 lxc.cgroup2.devices.deny = c 1:3 rwm

       then LXC would instruct the kernel to implement a denylist, i.e.
       the kernel will allow access to all devices not specifically
       denied in this list. This particular program states that no
       character devices or block devices might be created and that
       /dev/null is not allow allowed to be read, written, or created.

       Now consider the same program but followed by a "global rule"
       which determines the type of device program (allowlist or
       denylist) as explained above:

                 lxc.cgroup2.devices.allow = a
                 lxc.cgroup2.devices.deny = c *:* m
                 lxc.cgroup2.devices.deny = b *:* m
                 lxc.cgroup2.devices.deny = c 1:3 rwm
                 lxc.cgroup2.devices.allow = a

       The last line will cause LXC to reset the device list without
       changing the type of device program.

       If we specify:

                 lxc.cgroup2.devices.allow = a
                 lxc.cgroup2.devices.deny = c *:* m
                 lxc.cgroup2.devices.deny = b *:* m
                 lxc.cgroup2.devices.deny = c 1:3 rwm
                 lxc.cgroup2.devices.deny = a

       instead then the last line will cause LXC to reset the device list
       and switch from an allowlist program to a denylist program.

       lxc.cgroup.[controller name].[controller file]
              Specify the control group value to be set on a legacy
              cgroup hierarchy. The controller name is the literal name
              of the control group. The permitted names and the syntax of
              their values is not dictated by LXC, instead it depends on
              the features of the Linux kernel running at the time the
              container is started, eg.  lxc.cgroup.cpuset.cpus

       lxc.cgroup2.[controller name].[controller file]
              Specify the control group value to be set on the unified
              cgroup hierarchy. The controller name is the literal name
              of the control group. The permitted names and the syntax of
              their values is not dictated by LXC, instead it depends on
              the features of the Linux kernel running at the time the
              container is started, eg.  lxc.cgroup2.memory.high

       lxc.cgroup.dir
              specify a directory or path in which the container's cgroup
              will be created. For example, setting lxc.cgroup.dir =
              my-cgroup/first for a container named "c1" will create the
              container's cgroup as a sub-cgroup of "my-cgroup". For
              example, if the user's current cgroup "my-user" is located
              in the root cgroup of the cpuset controller in a cgroup v1
              hierarchy this would create the cgroup
              "/sys/fs/cgroup/cpuset/my-user/my-cgroup/first/c1" for the
              container. Any missing cgroups will be created by LXC. This
              presupposes that the user has write access to its current
              cgroup.

       lxc.cgroup.dir.container
              This is similar to lxc.cgroup.dir, but must be used
              together with lxc.cgroup.dir.monitor and affects only the
              container's cgroup path. This option is mutually exclusive
              with lxc.cgroup.dir.  Note that the final path the
              container attaches to may be extended further by the
              lxc.cgroup.dir.container.inner option.

       lxc.cgroup.dir.monitor
              This is the monitor process counterpart to
              lxc.cgroup.dir.container.

       lxc.cgroup.dir.monitor.pivot
              On container termination the PID of the monitor process is
              attached to this cgroup.  This path should not be a subpath
              of any other configured cgroup dir to ensure proper removal
              of other cgroup paths on container termination.

       lxc.cgroup.dir.container.inner
              Specify an additional subdirectory where the cgroup
              namespace will be created. With this option, the cgroup
              limits will be applied to the outer path specified in
              lxc.cgroup.dir.container, which is not accessible from
              within the container, making it possible to better enforce
              limits for privileged containers in a way they cannot
              override them.  This only works in conjunction with the
              lxc.cgroup.dir.container and lxc.cgroup.dir.monitor options
              and has otherwise no effect.

       lxc.cgroup.relative
              Set this to 1 to instruct LXC to never escape to the root
              cgroup. This makes it easy for users to adhere to
              restrictions enforced by cgroup2 and systemd. Specifically,
              this makes it possible to run LXC containers as systemd
              services.

   CAPABILITIES
       The capabilities can be dropped in the container if this one is
       run as root.

       lxc.cap.drop
              Specify the capability to be dropped in the container. A
              single line defining several capabilities with a space
              separation is allowed. The format is the lower case of the
              capability definition without the "CAP_" prefix, eg.
              CAP_SYS_MODULE should be specified as sys_module. See
              capabilities(7).  If used with no value, lxc will clear any
              drop capabilities specified up to this point.

       lxc.cap.keep
              Specify the capability to be kept in the container. All
              other capabilities will be dropped. When a special value of
              "none" is encountered, lxc will clear any keep capabilities
              specified up to this point. A value of "none" alone can be
              used to drop all capabilities.

   NAMESPACES
       A namespace can be cloned (lxc.namespace.clone), kept
       (lxc.namespace.keep) or shared (lxc.namespace.share.[namespace
       identifier]).

       lxc.namespace.clone
              Specify namespaces which the container is supposed to be
              created with. The namespaces to create are specified as a
              space separated list. Each namespace must correspond to one
              of the standard namespace identifiers as seen in the
              /proc/PID/ns directory.  When lxc.namespace.clone is not
              explicitly set all namespaces supported by the kernel and
              the current configuration will be used.

              To create a new mount, net and ipc namespace set
              lxc.namespace.clone=mount net ipc.

       lxc.namespace.keep
              Specify namespaces which the container is supposed to
              inherit from the process that created it. The namespaces to
              keep are specified as a space separated list. Each
              namespace must correspond to one of the standard namespace
              identifiers as seen in the /proc/PID/ns directory.  The
              lxc.namespace.keep is a denylist option, i.e. it is useful
              when enforcing that containers must keep a specific set of
              namespaces.

              To keep the network, user and ipc namespace set
              lxc.namespace.keep=user net ipc.

              Note that sharing pid namespaces will likely not work with
              most init systems.

              Note that if the container requests a new user namespace
              and the container wants to inherit the network namespace it
              needs to inherit the user namespace as well.

       lxc.namespace.share.[namespace identifier]
              Specify a namespace to inherit from another container or
              process.  The [namespace identifier] suffix needs to be
              replaced with one of the namespaces that appear in the
              /proc/PID/ns directory.

              To inherit the namespace from another process set the
              lxc.namespace.share.[namespace identifier] to the PID of
              the process, e.g. lxc.namespace.share.net=42.

              To inherit the namespace from another container set the
              lxc.namespace.share.[namespace identifier] to the name of
              the container, e.g. lxc.namespace.share.pid=c3.

              To inherit the namespace from another container located in
              a different path than the standard liblxc path set the
              lxc.namespace.share.[namespace identifier] to the full path
              to the container, e.g.  lxc.namespace.share.user=/opt/c3.

              In order to inherit namespaces the caller needs to have
              sufficient privilege over the process or container.

              Note that sharing pid namespaces between system containers
              will likely not work with most init systems.

              Note that if two processes are in different user namespaces
              and one process wants to inherit the other's network
              namespace it usually needs to inherit the user namespace as
              well.

              Note that without careful additional configuration of an
              LSM, sharing user+pid namespaces with a task may allow that
              task to escalate privileges to that of the task calling
              liblxc.

       lxc.time.offset.boot
              Specify a positive or negative offset for the boottime
              clock. The format accepts hours (h), minutes (m), seconds
              (s), milliseconds (ms), microseconds (us), and nanoseconds
              (ns).

       lxc.time.offset.monotonic
              Specify a positive or negative offset for the monotonic
              clock. The format accepts hours (h), minutes (m), seconds
              (s), milliseconds (ms), microseconds (us), and nanoseconds
              (ns).

   RESOURCE LIMITS
       The soft and hard resource limits for the container can be
       changed.  Unprivileged containers can only lower them. Resources
       which are not explicitly specified will be inherited.

       lxc.prlimit.[limit name]
              Specify the resource limit to be set. A limit is specified
              as two colon separated values which are either numeric or
              the word 'unlimited'. A single value can be used as a
              shortcut to set both soft and hard limit to the same value.
              The permitted names the "RLIMIT_" resource names in
              lowercase without the "RLIMIT_" prefix, eg. RLIMIT_NOFILE
              should be specified as "nofile". See setrlimit(2).  If used
              with no value, lxc will clear the resource limit specified
              up to this point. A resource with no explicitly configured
              limitation will be inherited from the process starting up
              the container.

   SYSCTL
       Configure kernel parameters for the container.

       lxc.sysctl.[kernel parameters name]
              Specify the kernel parameters to be set. The parameters
              available are those listed under /proc/sys/.  Note that not
              all sysctls are namespaced. Changing Non-namespaced sysctls
              will cause the system-wide setting to be modified.
              sysctl(8).  If used with no value, lxc will clear the
              parameters specified up to this point.

   APPARMOR PROFILE
       If lxc was compiled and installed with apparmor support, and the
       host system has apparmor enabled, then the apparmor profile under
       which the container should be run can be specified in the
       container configuration. The default is lxc-container-default-cgns
       if the host kernel is cgroup namespace aware, or lxc-container-
       default otherwise.

       lxc.apparmor.profile
              Specify the apparmor profile under which the container
              should be run. To specify that the container should be
              unconfined, use

              lxc.apparmor.profile = unconfined

              If the apparmor profile should remain unchanged (i.e. if
              you are nesting containers and are already confined), then
              use

              lxc.apparmor.profile = unchanged

              If you instruct LXC to generate the apparmor profile, then
              use

              lxc.apparmor.profile = generated

       lxc.apparmor.allow_incomplete
              Apparmor profiles are pathname based. Therefore many file
              restrictions require mount restrictions to be effective
              against a determined attacker. However, these mount
              restrictions are not yet implemented in the upstream
              kernel. Without the mount restrictions, the apparmor
              profiles still protect against accidental damager.

              If this flag is 0 (default), then the container will not be
              started if the kernel lacks the apparmor mount features, so
              that a regression after a kernel upgrade will be detected.
              To start the container under partial apparmor protection,
              set this flag to 1.

       lxc.apparmor.allow_nesting
              If set this to 1, causes the following changes. When
              generated apparmor profiles are used, they will contain the
              necessary changes to allow creating a nested container. In
              addition to the usual mount points, /dev/.lxc/proc and
              /dev/.lxc/sys will contain procfs and sysfs mount points
              without the lxcfs overlays, which, if generated apparmor
              profiles are being used, will not be read/writable
              directly.

       lxc.apparmor.raw
              A list of raw AppArmor profile lines to append to the
              profile. Only valid when using generated profiles.

   SELINUX CONTEXT
       If lxc was compiled and installed with SELinux support, and the
       host system has SELinux enabled, then the SELinux context under
       which the container should be run can be specified in the
       container configuration. The default is unconfined_t, which means
       that lxc will not attempt to change contexts.  See
       /usr/share/lxc/selinux/lxc.te for an example policy and more
       information.

       lxc.selinux.context
              Specify the SELinux context under which the container
              should be run or unconfined_t. For example

              lxc.selinux.context = system_u:system_r:lxc_t:s0:c22

       lxc.selinux.context.keyring
              Specify the SELinux context under which the container's
              keyring should be created. By default this the same as
              lxc.selinux.context, or the context lxc is executed under
              if lxc.selinux.context has not been set.

              lxc.selinux.context.keyring = system_u:system_r:lxc_t:s0:c22

   KERNEL KEYRING
       The Linux Keyring facility is primarily a way for various kernel
       components to retain or cache security data, authentication keys,
       encryption keys, and other data in the kernel. By default lxc will
       create a new session keyring for the started application.

       lxc.keyring.session
              Disable the creation of new session keyring by lxc. The
              started application will then inherit the current session
              keyring.  By default, or when passing the value 1, a new
              keyring will be created.

              lxc.keyring.session = 0

   SECCOMP CONFIGURATION
       A container can be started with a reduced set of available system
       calls by loading a seccomp profile at startup. The seccomp
       configuration file must begin with a version number on the first
       line, a policy type on the second line, followed by the
       configuration.

       Versions 1 and 2 are currently supported. In version 1, the policy
       is a simple allowlist. The second line therefore must read
       "allowlist", with the rest of the file containing one (numeric)
       syscall number per line. Each syscall number is allowlisted, while
       every unlisted number is denylisted for use in the container

       In version 2, the policy may be denylist or allowlist, supports
       per-rule and per-policy default actions, and supports per-
       architecture system call resolution from textual names.

       An example denylist policy, in which all system calls are allowed
       except for mknod, which will simply do nothing and return 0
       (success), looks like:

             2
             denylist
             mknod errno 0
             ioctl notify

       Specifying "errno" as action will cause LXC to register a seccomp
       filter that will cause a specific errno to be returned to the
       caller. The errno value can be specified after the "errno" action
       word.

       Specifying "notify" as action will cause LXC to register a seccomp
       listener and retrieve a listener file descriptor from the kernel.
       When a syscall is made that is registered as "notify" the kernel
       will generate a poll event and send a message over the file
       descriptor. The caller can read this message, inspect the syscalls
       including its arguments. Based on this information the caller is
       expected to send back a message informing the kernel which action
       to take. Until that message is sent the kernel will block the
       calling process. The format of the messages to read and sent is
       documented in seccomp itself.

       lxc.seccomp.profile
              Specify a file containing the seccomp configuration to load
              before the container starts.

       lxc.seccomp.allow_nesting
              If this flag is set to 1, then seccomp filters will be
              stacked regardless of whether a seccomp profile is already
              loaded.  This allows nested containers to load their own
              seccomp profile.  The default setting is 0.

       lxc.seccomp.notify.proxy
              Specify a unix socket to which LXC will connect and forward
              seccomp events to. The path must be in the form
              unix:/path/to/socket or unix:@socket. The former specifies
              a path-bound unix domain socket while the latter specifies
              an abstract unix domain socket.

       lxc.seccomp.notify.cookie
              An additional string sent along with proxied seccomp
              notification requests.

   PR_SET_NO_NEW_PRIVS
       With PR_SET_NO_NEW_PRIVS active execve() promises not to grant
       privileges to do anything that could not have been done without
       the execve() call (for example, rendering the set-user-ID and set-
       group-ID mode bits, and file capabilities non-functional).  Once
       set, this bit cannot be unset. The setting of this bit is
       inherited by children created by fork() and clone(), and preserved
       across execve().  Note that PR_SET_NO_NEW_PRIVS is applied after
       the container has changed into its intended AppArmor profile or
       SElinux context.

       lxc.no_new_privs
              Specify whether the PR_SET_NO_NEW_PRIVS flag should be set
              for the container. Set to 1 to activate.

   UID MAPPINGS
       A container can be started in a private user namespace with user
       and group id mappings. For instance, you can map userid 0 in the
       container to userid 200000 on the host. The root user in the
       container will be privileged in the container, but unprivileged on
       the host. Normally a system container will want a range of ids, so
       you would map, for instance, user and group ids 0 through 20,000
       in the container to the ids 200,000 through 220,000.

       lxc.idmap
              Four values must be provided. First a character, either
              'u', or 'g', to specify whether user or group ids are being
              mapped. Next is the first userid as seen in the user
              namespace of the container. Next is the userid as seen on
              the host. Finally, a range indicating the number of
              consecutive ids to map.

   CONTAINER HOOKS
       Container hooks are programs or scripts which can be executed at
       various times in a container's lifetime.

       When a container hook is executed, additional information is
       passed along. The lxc.hook.version argument can be used to
       determine if the following arguments are passed as command line
       arguments or through environment variables. The arguments are:

       • Container name.

       • Section (always 'lxc').

       • The hook type (i.e. 'clone' or 'pre-mount').

       • Additional arguments. In the case of the clone hook, any extra
         arguments passed will appear as further arguments to the hook.
         In the case of the stop hook, paths to filedescriptors for each
         of the container's namespaces along with their types are passed.

       The following environment variables are set:

       • LXC_CGNS_AWARE: indicator whether the container is cgroup
         namespace aware.

       • LXC_CONFIG_FILE: the path to the container configuration file.

       • LXC_HOOK_TYPE: the hook type (e.g. 'clone', 'mount', 'pre-
         mount'). Note that the existence of this environment variable is
         conditional on the value of lxc.hook.version. If it is set to 1
         then LXC_HOOK_TYPE will be set.

       • LXC_HOOK_SECTION: the section type (e.g. 'lxc', 'net'). Note
         that the existence of this environment variable is conditional
         on the value of lxc.hook.version. If it is set to 1 then
         LXC_HOOK_SECTION will be set.

       • LXC_HOOK_VERSION: the version of the hooks. This value is
         identical to the value of the container's lxc.hook.version
         config item. If it is set to 0 then old-style hooks are used. If
         it is set to 1 then new-style hooks are used.

       • LXC_LOG_LEVEL: the container's log level.

       • LXC_NAME: is the container's name.

       • LXC_[NAMESPACE IDENTIFIER]_NS: path under /proc/PID/fd/ to a
         file descriptor referring to the container's namespace. For each
         preserved namespace type there will be a separate environment
         variable. These environment variables will only be set if
         lxc.hook.version is set to 1.

       • LXC_ROOTFS_MOUNT: the path to the mounted root filesystem.

       • LXC_ROOTFS_PATH: this is the lxc.rootfs.path entry for the
         container. Note this is likely not where the mounted rootfs is
         to be found, use LXC_ROOTFS_MOUNT for that.

       • LXC_SRC_NAME: in the case of the clone hook, this is the
         original container's name.

       Standard output from the hooks is logged at debug level.  Standard
       error is not logged, but can be captured by the hook redirecting
       its standard error to standard output.

       lxc.hook.version
              To pass the arguments in new style via environment
              variables set to 1 otherwise set to 0 to pass them as
              arguments.  This setting affects all hooks arguments that
              were traditionally passed as arguments to the script.
              Specifically, it affects the container name, section (e.g.
              'lxc', 'net') and hook type (e.g.  'clone', 'mount', 'pre-
              mount') arguments. If new-style hooks are used then the
              arguments will be available as environment variables.  The
              container name will be set in LXC_NAME. (This is set
              independently of the value used for this config item.) The
              section will be set in LXC_HOOK_SECTION and the hook type
              will be set in LXC_HOOK_TYPE.  It also affects how the
              paths to file descriptors referring to the container's
              namespaces are passed. If set to 1 then for each namespace
              a separate environment variable LXC_[NAMESPACE
              IDENTIFIER]_NS will be set. If set to 0 then the paths will
              be passed as arguments to the stop hook.

       lxc.hook.pre-start
              A hook to be run in the host's namespace before the
              container ttys, consoles, or mounts are up.

       lxc.hook.pre-mount
              A hook to be run in the container's fs namespace but before
              the rootfs has been set up. This allows for manipulation of
              the rootfs, i.e. to mount an encrypted filesystem. Mounts
              done in this hook will not be reflected on the host (apart
              from mounts propagation), so they will be automatically
              cleaned up when the container shuts down.

       lxc.hook.mount
              A hook to be run in the container's namespace after
              mounting has been done, but before the pivot_root.

       lxc.hook.autodev
              A hook to be run in the container's namespace after
              mounting has been done and after any mount hooks have run,
              but before the pivot_root, if lxc.autodev == 1.  The
              purpose of this hook is to assist in populating the /dev
              directory of the container when using the autodev option
              for systemd based containers. The container's /dev
              directory is relative to the ${LXC_ROOTFS_MOUNT}
              environment variable available when the hook is run.

       lxc.hook.start-host
              A hook to be run in the host's namespace after the
              container has been setup, and immediately before starting
              the container init.

       lxc.hook.start
              A hook to be run in the container's namespace immediately
              before executing the container's init. This requires the
              program to be available in the container.

       lxc.hook.stop
              A hook to be run in the host's namespace with references to
              the container's namespaces after the container has been
              shut down. For each namespace an extra argument is passed
              to the hook containing the namespace's type and a filename
              that can be used to obtain a file descriptor to the
              corresponding namespace, separated by a colon. The type is
              the name as it would appear in the /proc/PID/ns directory.
              For instance for the mount namespace the argument usually
              looks like mnt:/proc/PID/fd/12.

       lxc.hook.post-stop
              A hook to be run in the host's namespace after the
              container has been shut down.

       lxc.hook.clone
              A hook to be run when the container is cloned to a new one.
              See lxc-clone(1) for more information.

       lxc.hook.destroy
              A hook to be run when the container is destroyed.

   CONTAINER HOOKS ENVIRONMENT VARIABLES
       A number of environment variables are made available to the
       startup hooks to provide configuration information and assist in
       the functioning of the hooks. Not all variables are valid in all
       contexts. In particular, all paths are relative to the host system
       and, as such, not valid during the lxc.hook.start hook.

       LXC_NAME
              The LXC name of the container. Useful for logging messages
              in common log environments. [-n]

       LXC_CONFIG_FILE
              Host relative path to the container configuration file.
              This gives the container to reference the original, top
              level, configuration file for the container in order to
              locate any additional configuration information not
              otherwise made available. [-f]

       LXC_CONSOLE
              The path to the console output of the container if not
              NULL.  [-c] [lxc.console.path]

       LXC_CONSOLE_LOGPATH
              The path to the console log output of the container if not
              NULL.  [-L]

       LXC_ROOTFS_MOUNT
              The mount location to which the container is initially
              bound.  This will be the host relative path to the
              container rootfs for the container instance being started
              and is where changes should be made for that instance.
              [lxc.rootfs.mount]

       LXC_ROOTFS_PATH
              The host relative path to the container root which has been
              mounted to the rootfs.mount location.  [lxc.rootfs.path]

       LXC_SRC_NAME
              Only for the clone hook. Is set to the original container
              name.

       LXC_TARGET
              Only for the stop hook. Is set to "stop" for a container
              shutdown or "reboot" for a container reboot.

       LXC_CGNS_AWARE
              If unset, then this version of lxc is not aware of cgroup
              namespaces. If set, it will be set to 1, and lxc is aware
              of cgroup namespaces. Note this does not guarantee that
              cgroup namespaces are enabled in the kernel. This is used
              by the lxcfs mount hook.

   LOGGING
       Logging can be configured on a per-container basis. By default,
       depending upon how the lxc package was compiled, container startup
       is logged only at the ERROR level, and logged to a file named
       after the container (with '.log' appended) either under the
       container path, or under /var/log/lxc.

       Both the default log level and the log file can be specified in
       the container configuration file, overriding the default behavior.
       Note that the configuration file entries can in turn be overridden
       by the command line options to lxc-start.

       lxc.log.level
              The level at which to log. The log level is an integer in
              the range of 0..8 inclusive, where a lower number means
              more verbose debugging. In particular 0 = trace, 1 = debug,
              2 = info, 3 = notice, 4 = warn, 5 = error, 6 = critical, 7
              = alert, and 8 = fatal. If unspecified, the level defaults
              to 5 (error), so that only errors and above are logged.

              Note that when a script (such as either a hook script or a
              network interface up or down script) is called, the
              script's standard output is logged at level 1, debug.

       lxc.log.file
              The file to which logging info should be written.

       lxc.log.syslog
              Send logging info to syslog. It respects the log level
              defined in lxc.log.level. The argument should be the syslog
              facility to use, valid ones are: daemon, local0, local1,
              local2, local3, local4, local5, local5, local6, local7.

   AUTOSTART
       The autostart options support marking which containers should be
       auto-started and in what order. These options may be used by LXC
       tools directly or by external tooling provided by the
       distributions.

       lxc.start.auto
              Whether the container should be auto-started.  Valid values
              are 0 (off) and 1 (on).

       lxc.start.delay
              How long to wait (in seconds) after the container is
              started before starting the next one.

       lxc.start.order
              An integer used to sort the containers when auto-starting a
              series of containers at once. A lower value means an
              earlier start.

       lxc.monitor.unshare
              If not zero the mount namespace will be unshared from the
              host before initializing the container (before running any
              pre-start hooks). This requires the CAP_SYS_ADMIN
              capability at startup.  Default is 0.

       lxc.monitor.signal.pdeath
              Set the signal to be sent to the container's init when the
              lxc monitor exits. By default it is set to SIGKILL which
              will cause all container processes to be killed when the
              lxc monitor process dies.  To ensure that containers stay
              alive even if lxc monitor dies set this to 0.

       lxc.group
              A multi-value key (can be used multiple times) to put the
              container in a container group. Those groups can then be
              used (amongst other things) to start a series of related
              containers.

   AUTOSTART AND SYSTEM BOOT
       Each container can be part of any number of groups or no group at
       all.  Two groups are special. One is the NULL group, i.e. the
       container does not belong to any group. The other group is the
       "onboot" group.

       When the system boots with the LXC service enabled, it will first
       attempt to boot any containers with lxc.start.auto == 1 that is a
       member of the "onboot" group. The startup will be in order of
       lxc.start.order.  If an lxc.start.delay has been specified, that
       delay will be honored before attempting to start the next
       container to give the current container time to begin
       initialization and reduce overloading the host system. After
       starting the members of the "onboot" group, the LXC system will
       proceed to boot containers with lxc.start.auto == 1 which are not
       members of any group (the NULL group) and proceed as with the
       onboot group.

   CONTAINER ENVIRONMENT
       If you want to pass environment variables into the container (that
       is, environment variables which will be available to init and all
       of its descendents), you can use lxc.environment parameters to do
       so. Be careful that you do not pass in anything sensitive; any
       process in the container which doesn't have its environment
       scrubbed will have these variables available to it, and
       environment variables are always available via /proc/PID/environ.

       Subkeys are available to narrow the scope of environment
       variables: lxc.environment.runtime applies only to the container's
       init process (and all its descendents), and lxc.environment.hooks
       applies only to hooks.

       These configuration parameters can be specified multiple times;
       once for each environment variable you wish to configure.

       lxc.environment
              Environment variables applied both to the container init
              process and to hooks. Example:

                            lxc.environment = APP_ENV=production
                            lxc.environment = SYSLOG_SERVER=192.0.2.42

              It is possible to inherit host environment variables by
              setting the name of the variable without a "=" sign. For
              example:

                            lxc.environment = PATH

       lxc.environment.runtime
              Environment variables applied only to the container's init
              process.

       lxc.environment.hooks
              Environment variables applied only to hooks.
EXAMPLES         top
       In addition to the few examples given below, you will find some
       other examples of configuration file in
       /usr/share/doc/lxc/examples

   NETWORK
       This configuration sets up a container to use a veth pair device
       with one side plugged to a bridge br0 (which has been configured
       before on the system by the administrator). The virtual network
       device visible in the container is renamed to eth0.

               lxc.uts.name = myhostname
               lxc.net.0.type = veth
               lxc.net.0.flags = up
               lxc.net.0.link = br0
               lxc.net.0.name = eth0
               lxc.net.0.hwaddr = 4a:49:43:49:79:bf
               lxc.net.0.ipv4.address = 10.2.3.5/24 10.2.3.255
               lxc.net.0.ipv6.address = 2003:db8:1:0:214:1234:fe0b:3597

   UID/GID MAPPING
       This configuration will map both user and group ids in the range
       0-9999 in the container to the ids 100000-109999 on the host.

               lxc.idmap = u 0 100000 10000
               lxc.idmap = g 0 100000 10000

   CONTROL GROUP
       This configuration will setup several control groups for the
       application, cpuset.cpus restricts usage of the defined cpu,
       cpus.share prioritize the control group, devices.allow makes
       usable the specified devices.

               lxc.cgroup.cpuset.cpus = 0,1
               lxc.cgroup.cpu.shares = 1234
               lxc.cgroup.devices.deny = a
               lxc.cgroup.devices.allow = c 1:3 rw
               lxc.cgroup.devices.allow = b 8:0 rw

   COMPLEX CONFIGURATION
       This example show a complex configuration making a complex network
       stack, using the control groups, setting a new hostname, mounting
       some locations and a changing root file system.

               lxc.uts.name = complex
               lxc.net.0.type = veth
               lxc.net.0.flags = up
               lxc.net.0.link = br0
               lxc.net.0.hwaddr = 4a:49:43:49:79:bf
               lxc.net.0.ipv4.address = 10.2.3.5/24 10.2.3.255
               lxc.net.0.ipv6.address = 2003:db8:1:0:214:1234:fe0b:3597
               lxc.net.0.ipv6.address = 2003:db8:1:0:214:5432:feab:3588
               lxc.net.1.type = macvlan
               lxc.net.1.flags = up
               lxc.net.1.link = eth0
               lxc.net.1.hwaddr = 4a:49:43:49:79:bd
               lxc.net.1.ipv4.address = 10.2.3.4/24
               lxc.net.1.ipv4.address = 192.168.10.125/24
               lxc.net.1.ipv6.address = 2003:db8:1:0:214:1234:fe0b:3596
               lxc.net.2.type = phys
               lxc.net.2.flags = up
               lxc.net.2.link = random0
               lxc.net.2.hwaddr = 4a:49:43:49:79:ff
               lxc.net.2.ipv4.address = 10.2.3.6/24
               lxc.net.2.ipv6.address = 2003:db8:1:0:214:1234:fe0b:3297
               lxc.cgroup.cpuset.cpus = 0,1
               lxc.cgroup.cpu.shares = 1234
               lxc.cgroup.devices.deny = a
               lxc.cgroup.devices.allow = c 1:3 rw
               lxc.cgroup.devices.allow = b 8:0 rw
               lxc.mount.fstab = /etc/fstab.complex
               lxc.mount.entry = /lib /root/myrootfs/lib none ro,bind 0 0
               lxc.rootfs.path = dir:/mnt/rootfs.complex
               lxc.rootfs.options = idmap=container
               lxc.cap.drop = sys_module mknod setuid net_raw
               lxc.cap.drop = mac_override
SEE ALSO         top
       chroot(1), pivot_root(8), fstab(5), capabilities(7)
SEE ALSO         top
       lxc(7), lxc-create(1), lxc-copy(1), lxc-destroy(1), lxc-start(1),
       lxc-stop(1), lxc-execute(1), lxc-console(1), lxc-monitor(1),
       lxc-wait(1), lxc-cgroup(1), lxc-ls(1), lxc-info(1), lxc-freeze(1),
       lxc-unfreeze(1), lxc-attach(1), lxc.conf(5)
COLOPHON         top
       This page is part of the lxc (Linux containers) project.
       Information about the project can be found at 
       ⟨http://linuxcontainers.org/⟩.  If you have a bug report for this
       manual page, send it to lxc-devel@lists.linuxcontainers.org.  This
       page was obtained from the project's upstream Git repository
       ⟨https://github.com/lxc/lxc.git⟩ on 2026-05-24.  (At that time,
       the date of the most recent commit that was found in the
       repository was 2026-05-21.)  If you discover any rendering
       problems in this HTML version of the page, or you believe there is
       a better or more up-to-date source for the page, or you have
       corrections or improvements to the information in this COLOPHON
       (which is not part of the original manual page), send a mail to
       man-pages@man7.org

                                2026-04-29          lxc.container.conf(5)
Pages that refer to this page: lxc.conf(5),  lxc.system.conf(5)

HTML rendering created 2026-05-30 by Michael Kerrisk, author of The Linux Programming Interface.

For details of in-depth Linux/UNIX system programming training courses that I teach, look here.

Hosting by jambit GmbH.

Cover of TLPI
