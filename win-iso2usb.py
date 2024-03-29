import os


def run(command: str) -> str:
    stream = os.popen(command)
    output = stream.read()
    return output

def get_usb_device_path() -> str:
    disks = run('diskutil list').split('\n')
    for line in disks:
        if ' (external, physical)' in line:
            device_path, _ = line.split(' (external, physical)')
            return device_path
    return 'not found'

DEVICE = input(f'USB device path ({get_usb_device_path()}): ') or get_usb_device_path()
WINDOWS_ISO_PATH = input('ISO file path (~/Downloads/LB2CFRE_EN_DVD.iso): ') or '~/Downloads/LB2CFRE_EN_DVD.iso'

agree = input('All files on your usb-flash will be destroyed. Press "Y" if you shure: ').lower()
if agree != 'y':
    print('Operation not permitted')
    exit()

run(f'diskutil eraseDisk MS-DOS WININST MBR {DEVICE}')
mount_iso = run(f'hdiutil mount {WINDOWS_ISO_PATH}')
_, mount_iso_path = mount_iso.replace('\n', '').split('/Volumes/')

print('Copying files. part 1')
run(f'rsync -avh --progress --exclude=sources/install.wim /Volumes/{mount_iso_path}/ /Volumes/WININST')

print('Installing dependecies')
run('xcode-select --install')
run('brew install wimlib')

print('Copying files. part 2')
run(f'wimlib-imagex split /Volumes/{mount_iso_path}/sources/install.wim /Volumes/WININST/sources/install.swm 3000')

print('Unmounting iso')
run(f'umount /Volumes/{mount_iso_path}')

print('Done')
