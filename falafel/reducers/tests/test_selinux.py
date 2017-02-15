from ..selinux import SELinux
from ...mappers.grub_conf import GrubConfig
from ...mappers.selinux_config import SelinuxConfig
from ...mappers.sestatus import SEStatus
from ...tests import context_wrap

GRUB_DISABLED = 'grub_disabled'
GRUB_NOT_ENFORCING = 'grub_not_enforcing'
RUNTIME_DISABLED = 'sestatus_disabled'
RUNTIME_NOT_ENFORCING = 'sestatus_not_enforcing'
BOOT_DISABLED = 'selinux_conf_disabled'
BOOT_NOT_ENFORCING = 'selinux_conf_not_enforcing'

SESTATUS_OUT = """
SELinux status:                 enabled
SELinuxfs mount:                /sys/fs/selinux
SELinux root directory:         /etc/selinux
Loaded policy name:             targeted
Current mode:                   enforcing
Mode from config file:          enforcing
Policy MLS status:              enabled
Policy deny_unknown status:     allowed
Max kernel policy version:      30
"""

SESTATUS_OUT_DISABLED = """
SELinux status:                 disabled
SELinuxfs mount:                /sys/fs/selinux
SELinux root directory:         /etc/selinux
Loaded policy name:             targeted
Current mode:                   enforcing
Mode from config file:          enforcing
Policy MLS status:              enabled
Policy deny_unknown status:     allowed
Max kernel policy version:      30
"""

SESTATUS_OUT_NOT_ENFORCING = """
SELinux status:                 enabled
SELinuxfs mount:                /sys/fs/selinux
SELinux root directory:         /etc/selinux
Loaded policy name:             targeted
Current mode:                   permissive
Mode from config file:          enforcing
Policy MLS status:              enabled
Policy deny_unknown status:     allowed
Max kernel policy version:      30
"""

SELINUX_CONF = """
# This file controls the state of SELinux on the system.
# SELINUX= can take one of these three values:
#     enforcing - SELinux security policy is enforced.
#     permissive - SELinux prints warnings instead of enforcing.
#     disabled - No SELinux policy is loaded.
SELINUX=enforcing
# SELINUXTYPE= can take one of these two values:
#     targeted - Targeted processes are protected,
#     mls - Multi Level Security protection.
SELINUXTYPE=targeted
"""

SELINUX_CONF_DISABLED = """
# This file controls the state of SELinux on the system.
# SELINUX= can take one of these three values:
#     enforcing - SELinux security policy is enforced.
#     permissive - SELinux prints warnings instead of enforcing.
#     disabled - No SELinux policy is loaded.
SELINUX=disabled
# SELINUXTYPE= can take one of these two values:
#     targeted - Targeted processes are protected,
#     mls - Multi Level Security protection.
SELINUXTYPE=targeted
"""

SELINUX_CONF_NOT_ENFORCING = """
# This file controls the state of SELinux on the system.
# SELINUX= can take one of these three values:
#     enforcing - SELinux security policy is enforced.
#     permissive - SELinux prints warnings instead of enforcing.
#     disabled - No SELinux policy is loaded.
SELINUX=permissive
# SELINUXTYPE= can take one of these two values:
#     targeted - Targeted processes are protected,
#     mls - Multi Level Security protection.
SELINUXTYPE=targeted
"""

SELINUX_CONFIGS = [
    (
        {'SELINUX': 'enforcing', 'SELINUXTYPE': 'targeted'},
        {},
    ),
    # Problem.
    (
        {'SELINUX': 'permissive', 'SELINUXTYPE': 'targeted'},
        {BOOT_NOT_ENFORCING: 'permissive'},
    ),
    # Another kind of problem.
    (
        {'SELINUX': 'disabled', 'SELINUXTYPE': 'targeted'},
        {BOOT_DISABLED: 'disabled'},
    ),
    # Changing value of SELINUXTYPE should have no effect.
    (
        {'SELINUX': 'enforcing', 'SELINUXTYPE': 'mls'},
        {},
    ),
    (
        {'SELINUX': 'permissive', 'SELINUXTYPE': 'blabla'},
        {BOOT_NOT_ENFORCING: 'permissive'},
    ),
    (
        {'SELINUX': 'disabled', 'SELINUXTYPE': 'barfoo'},
        {BOOT_DISABLED: 'disabled'},
    ),
]

SESTATUS_TEMPLATE = {
    'loaded_policy_name': 'targeted', 'selinux_root_directory': '/etc/selinux',
    'selinuxfs_mount': '/sys/fs/selinux', 'mode_from_config_file': 'enforcing',
    'policy_mls_status': 'enabled',
    'policy_deny_unknown_status': 'allowed', 'max_kernel_policy_version': '30'
}

SESTATUS_OUTPUTS = [
    # No problem.
    (
        {'selinux_status': 'enabled', 'current_mode': 'enforcing'},
        {},
    ),
    # Problematic.
    (
        {'selinux_status': 'disabled', 'current_mode': 'enforcing'},
        {RUNTIME_DISABLED: 'disabled'},
    ),
    (
        {'selinux_status': 'enabled', 'current_mode': 'permissive'},
        {RUNTIME_NOT_ENFORCING: 'permissive'},
    ),
    (
        {'selinux_status': 'disabled', 'current_mode': 'permissive'},
        {RUNTIME_DISABLED: 'disabled'},
    ),
]

# rhel-6
GRUB1_TEMPLATE = """
# grub.conf generated by anaconda
#
# Note that you do not have to rerun grub after making changes to this file
# NOTICE:  You have a /boot partition.  This means that
#          all kernel and initrd paths are relative to /boot/, eg.
#          root (hd0,0)
#          kernel /vmlinuz-version ro root=/dev/mapper/VolGroup-lv_root
#          initrd /initrd-[generic-]version.img
#boot=/dev/sda
default=0
timeout=5
splashimage=(hd0,0)/grub/splash.xpm.gz
hiddenmenu
title Red Hat Enterprise Linux 6 (2.6.32-642.el6.x86_64)
	root (hd0,0)
	kernel /vmlinuz-2.6.32-642.el6.x86_64 {kernel_boot_options} ro root=/dev/mapper/VolGroup-lv_root rd_NO_LUKS LANG=en_US.UTF-8 rd_NO_MD rd_LVM_LV=VolGroup/lv_swap SYSFONT=latarcyrheb-sun16 crashkernel=auto rd_LVM_LV=VolGroup/lv_root  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet
	initrd /initramfs-2.6.32-642.el6.x86_64.img
"""  # noqa


GRUB1_OUTPUTS = [
    # noqa
    # No problem.
    (
        {'kernel_boot_options': ''},
        {},
    ),
    # Problematic.
    (
        {'kernel_boot_options': 'selinux=0'},
        {GRUB_DISABLED: [
            '/vmlinuz-2.6.32-642.el6.x86_64 selinux=0 ro root=/dev/mapper/VolGroup-lv_root rd_NO_LUKS LANG=en_US.UTF-8 rd_NO_MD rd_LVM_LV=VolGroup/lv_swap SYSFONT=latarcyrheb-sun16 crashkernel=auto rd_LVM_LV=VolGroup/lv_root  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet',
        ]},
    ),
    (
        {'kernel_boot_options': 'enforcing=0'},
        {GRUB_NOT_ENFORCING: [
            '/vmlinuz-2.6.32-642.el6.x86_64 enforcing=0 ro root=/dev/mapper/VolGroup-lv_root rd_NO_LUKS LANG=en_US.UTF-8 rd_NO_MD rd_LVM_LV=VolGroup/lv_swap SYSFONT=latarcyrheb-sun16 crashkernel=auto rd_LVM_LV=VolGroup/lv_root  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet',
        ]},
    ),
    (
        {'kernel_boot_options': 'selinux=0 enforcing=0'},
        {
            GRUB_DISABLED: [
                '/vmlinuz-2.6.32-642.el6.x86_64 selinux=0 enforcing=0 ro root=/dev/mapper/VolGroup-lv_root rd_NO_LUKS LANG=en_US.UTF-8 rd_NO_MD rd_LVM_LV=VolGroup/lv_swap SYSFONT=latarcyrheb-sun16 crashkernel=auto rd_LVM_LV=VolGroup/lv_root  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet',
            ],
            GRUB_NOT_ENFORCING: [
                '/vmlinuz-2.6.32-642.el6.x86_64 selinux=0 enforcing=0 ro root=/dev/mapper/VolGroup-lv_root rd_NO_LUKS LANG=en_US.UTF-8 rd_NO_MD rd_LVM_LV=VolGroup/lv_swap SYSFONT=latarcyrheb-sun16 crashkernel=auto rd_LVM_LV=VolGroup/lv_root  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet',
            ]
        },
    ),
]

# rhel-7
GRUB2_TEMPLATE = """
#
# DO NOT EDIT THIS FILE
#
# It is automatically generated by grub2-mkconfig using templates
# from /etc/grub.d and settings from /etc/default/grub
#

### BEGIN /etc/grub.d/00_header ###
set pager=1

if [ -s $prefix/grubenv ]; then
  load_env
fi
if [ "${next_entry}" ] ; then
   set default="${next_entry}"
   set next_entry=
   save_env next_entry
   set boot_once=true
else
   set default="${saved_entry}"
fi

if [ x"${feature_menuentry_id}" = xy ]; then
  menuentry_id_option="--id"
else
  menuentry_id_option=""
fi

export menuentry_id_option

if [ "${prev_saved_entry}" ]; then
  set saved_entry="${prev_saved_entry}"
  save_env saved_entry
  set prev_saved_entry=
  save_env prev_saved_entry
  set boot_once=true
fi

function savedefault {
  if [ -z "${boot_once}" ]; then
    saved_entry="${chosen}"
    save_env saved_entry
  fi
}

function load_video {
  if [ x$feature_all_video_module = xy ]; then
    insmod all_video
  else
    insmod efi_gop
    insmod efi_uga
    insmod ieee1275_fb
    insmod vbe
    insmod vga
    insmod video_bochs
    insmod video_cirrus
  fi
}

terminal_output console
if [ x$feature_timeout_style = xy ] ; then
  set timeout_style=menu
  set timeout=5
# Fallback normal timeout code in case the timeout_style feature is
# unavailable.
else
  set timeout=5
fi
### END /etc/grub.d/00_header ###

### BEGIN /etc/grub.d/00_tuned ###
set tuned_params=""
### END /etc/grub.d/00_tuned ###

### BEGIN /etc/grub.d/01_users ###
if [ -f ${prefix}/user.cfg ]; then
  source ${prefix}/user.cfg
  if [ -n ${GRUB2_PASSWORD} ]; then
    set superusers="root"
    export superusers
    password_pbkdf2 root ${GRUB2_PASSWORD}
  fi
fi
### END /etc/grub.d/01_users ###

### BEGIN /etc/grub.d/10_linux ###
menuentry 'Red Hat Enterprise Linux Server (3.10.0-327.el7.x86_64) 7.2 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-327.el7.x86_64-advanced-4f80b3d4-90ba-4545-869c-febdecc586ce' {
	load_video
	set gfxpayload=keep
	insmod gzio
	insmod part_msdos
	insmod xfs
	set root='hd0,msdos1'
	if [ x$feature_platform_search_hint = xy ]; then
	  search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdos1 --hint-baremetal=ahci0,msdos1 --hint='hd0,msdos1'  860a7b56-dbdd-498a-b085-53dc93e4650b
	else
	  search --no-floppy --fs-uuid --set=root 860a7b56-dbdd-498a-b085-53dc93e4650b
	fi
	linux16 /vmlinuz-3.10.0-327.el7.x86_64 %s root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8
	initrd16 /initramfs-3.10.0-327.el7.x86_64.img
}
menuentry 'Red Hat Enterprise Linux Server (0-rescue-9f20b35c9faa49aebe171f62a11b236f) 7.2 (Maipo)' --class red --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-0-rescue-9f20b35c9faa49aebe171f62a11b236f-advanced-4f80b3d4-90ba-4545-869c-febdecc586ce' {
	load_video
	insmod gzio
	insmod part_msdos
	insmod xfs
	set root='hd0,msdos1'
	if [ x$feature_platform_search_hint = xy ]; then
	  search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdos1 --hint-baremetal=ahci0,msdos1 --hint='hd0,msdos1'  860a7b56-dbdd-498a-b085-53dc93e4650b
	else
	  search --no-floppy --fs-uuid --set=root 860a7b56-dbdd-498a-b085-53dc93e4650b
	fi
	linux16 /vmlinuz-0-rescue-9f20b35c9faa49aebe171f62a11b236f %s root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet
	initrd16 /initramfs-0-rescue-9f20b35c9faa49aebe171f62a11b236f.img
}

### END /etc/grub.d/10_linux ###

### BEGIN /etc/grub.d/20_linux_xen ###
### END /etc/grub.d/20_linux_xen ###

### BEGIN /etc/grub.d/20_ppc_terminfo ###
### END /etc/grub.d/20_ppc_terminfo ###

### BEGIN /etc/grub.d/30_os-prober ###
### END /etc/grub.d/30_os-prober ###

### BEGIN /etc/grub.d/40_custom ###
# This file provides an easy way to add custom menu entries.  Simply type the
# menu entries you want to add after this comment.  Be careful not to change
# the 'exec tail' line above.
### END /etc/grub.d/40_custom ###

### BEGIN /etc/grub.d/41_custom ###
if [ -f  ${config_directory}/custom.cfg ]; then
  source ${config_directory}/custom.cfg
elif [ -z "${config_directory}" -a -f  $prefix/custom.cfg ]; then
  source $prefix/custom.cfg;
fi
### END /etc/grub.d/41_custom ###
"""  # noqa

GRUB2_OUTPUTS = [
    # No problem.
    (
        {'kernel_boot_options': ''},
        {},
    ),
    # Problematic.
    (
        {'kernel_boot_options': 'selinux=0'},
        {GRUB_DISABLED: [
            '/vmlinuz-3.10.0-327.el7.x86_64 selinux=0 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8',
            '/vmlinuz-0-rescue-9f20b35c9faa49aebe171f62a11b236f selinux=0 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet',
        ]},
    ),
    (
        {'kernel_boot_options': 'enforcing=0'},
        {GRUB_NOT_ENFORCING: [
            '/vmlinuz-3.10.0-327.el7.x86_64 enforcing=0 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8',
            '/vmlinuz-0-rescue-9f20b35c9faa49aebe171f62a11b236f enforcing=0 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet',
        ]},
    ),
    (
        {'kernel_boot_options': 'selinux=0 enforcing=0'},
        {
            GRUB_DISABLED: [
                '/vmlinuz-3.10.0-327.el7.x86_64 selinux=0 enforcing=0 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8',
                '/vmlinuz-0-rescue-9f20b35c9faa49aebe171f62a11b236f selinux=0 enforcing=0 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet',
            ],
            GRUB_NOT_ENFORCING: [
                '/vmlinuz-3.10.0-327.el7.x86_64 selinux=0 enforcing=0 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8',
                '/vmlinuz-0-rescue-9f20b35c9faa49aebe171f62a11b236f selinux=0 enforcing=0 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet',
            ]
        },
    ),
]

TEST_CASES = [
    ((SESTATUS_OUT, SELINUX_CONF, GRUB1_TEMPLATE),
     (True, {})),
    ((SESTATUS_OUT, SELINUX_CONF, GRUB1_TEMPLATE.format(kernel_boot_options='selinux=0')),
     (False, {GRUB_DISABLED: ['/vmlinuz-2.6.32-642.el6.x86_64 selinux=0 ro root=/dev/mapper/VolGroup-lv_root rd_NO_LUKS LANG=en_US.UTF-8 rd_NO_MD rd_LVM_LV=VolGroup/lv_swap SYSFONT=latarcyrheb-sun16 crashkernel=auto rd_LVM_LV=VolGroup/lv_root  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet']})),
    ((SESTATUS_OUT, SELINUX_CONF, GRUB1_TEMPLATE.format(kernel_boot_options='enforcing=0')),
     (False, {GRUB_NOT_ENFORCING: ['/vmlinuz-2.6.32-642.el6.x86_64 enforcing=0 ro root=/dev/mapper/VolGroup-lv_root rd_NO_LUKS LANG=en_US.UTF-8 rd_NO_MD rd_LVM_LV=VolGroup/lv_swap SYSFONT=latarcyrheb-sun16 crashkernel=auto rd_LVM_LV=VolGroup/lv_root  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet']})),
    ((SESTATUS_OUT, SELINUX_CONF, GRUB2_TEMPLATE % ('selinux=0', 'selinux=0')),
     (False, {GRUB_DISABLED: ['/vmlinuz-3.10.0-327.el7.x86_64 selinux=0 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8',
                              '/vmlinuz-0-rescue-9f20b35c9faa49aebe171f62a11b236f selinux=0 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet',
                              ]})),
    ((SESTATUS_OUT_DISABLED, SELINUX_CONF, GRUB2_TEMPLATE),
     (False, {RUNTIME_DISABLED: 'disabled'})),
    ((SESTATUS_OUT_NOT_ENFORCING, SELINUX_CONF, GRUB2_TEMPLATE),
     (False, {RUNTIME_NOT_ENFORCING: 'permissive'})),
    ((SESTATUS_OUT, SELINUX_CONF_DISABLED, GRUB1_TEMPLATE),
     (False, {BOOT_DISABLED: 'disabled'})),
    ((SESTATUS_OUT, SELINUX_CONF_NOT_ENFORCING, GRUB1_TEMPLATE),
     (False, {BOOT_NOT_ENFORCING: 'permissive'})),
    ((SESTATUS_OUT_DISABLED, SELINUX_CONF_NOT_ENFORCING, GRUB1_TEMPLATE),
     (False, {RUNTIME_DISABLED: 'disabled', BOOT_NOT_ENFORCING: 'permissive'})),
    ((SESTATUS_OUT_NOT_ENFORCING, SELINUX_CONF_DISABLED, GRUB1_TEMPLATE.format(kernel_boot_options='selinux=0')),
     (False, {GRUB_DISABLED: ['/vmlinuz-2.6.32-642.el6.x86_64 selinux=0 ro root=/dev/mapper/VolGroup-lv_root rd_NO_LUKS LANG=en_US.UTF-8 rd_NO_MD rd_LVM_LV=VolGroup/lv_swap SYSFONT=latarcyrheb-sun16 crashkernel=auto rd_LVM_LV=VolGroup/lv_root  KEYBOARDTYPE=pc KEYTABLE=us rd_NO_DM rhgb quiet'],
              RUNTIME_NOT_ENFORCING: 'permissive',
              BOOT_DISABLED: 'disabled'
              })),
]


def test_integration():
    for inputs, outputs in TEST_CASES:
        sestatus = SEStatus(context_wrap(inputs[0]))
        selinux_config = SelinuxConfig(context_wrap(inputs[1]))
        grub_config = GrubConfig(context_wrap(inputs[2]))
        selinux = SELinux(None,
                          {SEStatus: sestatus,
                           SelinuxConfig: selinux_config,
                           GrubConfig: grub_config}
                          )
        assert selinux.ok() == outputs[0]
        assert selinux.problems == outputs[1]
        import pprint
        pprint.pprint(selinux.problems)