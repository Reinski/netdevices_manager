# Entry point for the application.
from . import app    # For application discovery by the 'flask' command.
from . import views  # For import side-effects of setting up routes.
from flask import flash
#from flask_socketio import SocketIO, emit
import os
import subprocess
import threading
import re

# The public key must be added to the target's authorized keys
# Also, the hostkeys must be known and trusted without prompting for confirmation
devices = {
    'octoprint': {'user': 'pi', 'sudo': 'sudo', },
    'raspberrypi': {'user': 'pi', 'sudo': 'sudo', },
}

commands = {
    'check': {'cmd': 'nc -vz {host} 22', 'ok': '.*succeeded.*', 'cmdname': 'check'},
    'reboot': {'cmd': 'ssh {user}@{host} {sudo} reboot now', 'cmdname': 'reboot'},
    'shutdown': {'cmd': 'ssh {user}@{host} {sudo} shutdown now', 'cmdname': 'shutdown'},
    'uptime': {'cmd': 'ssh {user}@{host} {sudo} uptime -s', 'cmdname': 'uptime'},
    'model': {'cmd': 'ssh {user}@{host} cat /proc/device-tree/model', 'cmdname': 'model'},
}

def query_device_status(device, dev_data):
    # check ssh connection
    result = execute_command(commands['check'], device, dev_data, False)
    dev_data['check-result'] = result
    if result.lower() == 'ok':
        # get uptime
        result = execute_command(commands['uptime'], device, dev_data, False)
        dev_data['uptime'] = result
        result = execute_command(commands['model'], device, dev_data, False)
        dev_data['model'] = result

def update_device_statuses():
    global devices
    tasks = []
    for device, dev_data in devices.items():
        trd = threading.Thread(target=query_device_status, args=(device, dev_data))
        tasks.append(trd)
        trd.start()
    for trd in tasks:
        trd.join()
    
def process_devices(action, sel_devices, generate_messages = True):
    """Performs the specified action on the specified devices.
       action:      one of the keys from the commands-dictionary
       sel_devices: list of keys from the devices dictionary
    """
    # get the command for the action
    cmd = commands.get(action, None)
    if not cmd:
        return "Unknown command: {}".format(action)
    # perform the action
    proc_devices = []
    for device in sel_devices:
        dev_data = devices.get(device)
        if dev_data:
            execute_command(cmd, device, dev_data, generate_messages)
            proc_devices.append(device)
    return "Sent {} command to: {}".format(action, ', '.join(proc_devices))

def execute_command(command, host, dev_data, do_flash = True):
    """Execute the specified command template by replacing the variables from host and dev_data.
       command:   command-template, usually from the commands dictionary
       host:      name or address of the host
       dev_data:  further data for the host/device which is used for replacements in the template
    """
    cmd = command['cmd'].format(host=host, **dev_data)
    print('executing: {0}'.format(cmd))
    process = subprocess.Popen(cmd.split(),
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if 'ok' in command:
        if not 'ok-regex' in command:
            # precompile
            command['ok-regex'] = re.compile(command['ok'])
        result = stdout.decode() + stderr.decode()
        if command['ok-regex'].match(result):
            if do_flash:
                flash("{0} {1}: OK".format(host, command["cmdname"]))
            return 'ok'
    if 'nok' in command:
        if not 'nok-regex' in command:
            # precompile
            command['nok-regex'] = re.compile(command['nok'])
        result = stdout.decode() + stderr.decode()
        if command['nok-regex'].match(result):
            if do_flash:
                flash("{0} {1}: NOK".format(host, command["cmdname"]))
            return 'nok'
    if stderr:
        if do_flash:
            flash("{0} {1}: {2}".format(host, command["cmdname"], command,stderr.decode()) )
        return stderr.decode()
    else:
        if do_flash:
            flash("{0} {1}: {2}".format(host, command["cmdname"], command,stdout.decode()) )
        return stdout.decode()

cfg = {}
cfg_file = os.environ.get('FLASK_APP_CONFIG', '')
if cfg_file:
    print(f"Loading config from {cfg_file}")
    import yaml
    with open(cfg_file, 'r') as stream:
        try:
            cfg = yaml.safe_load(stream)
            devices = cfg['devices']
        except yaml.YAMLError as exc:
            print(exc)
print(devices)
if __name__ == '__main__':
    print("starting server...")
    app.run(debug=True, host='0.0.0.0', port=4999)