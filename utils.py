from paramiko import SSHClient, AutoAddPolicy

def get_remote_files(dir_path='.'):
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect('gotsva1648.got.volvocars.net', username='hiluser')
    stdin, stdout, stderr = client.exec_command(f'ls -l {dir_path}')
    lines = stdout.read().splitlines()
    client.close()

    directories = [('folder', '.'), ('folder', '..')]
    files = []
    for line in lines:
        line = line.decode('utf-8')
        if line.startswith('d'):
            directories.append(('folder', line.split()[-1]))
        else:
            files.append(('file', line.split()[-1]))

    return directories + files

def load_rig_list():
    """
    """
    try:
        rig_list = ["gotsva1648.got.volvocars.net", "gotsva1678.got.volvocars.net", "gotsva1680.got.volvocars.net", "gotsva1670.got.volvocars.net"] 
        return rig_list
    except Exception as e:
        print(f"Failed to load rig list: {e}")
        return []
    
# Get node list ls /dev/ | grep -E 'ttyUSB';