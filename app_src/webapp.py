# Entry point for the application.
from . import app    # For application discovery by the 'flask' command.
from . import views  # For import side-effects of setting up routes.
from flask import flash
import subprocess
import re

devices = {
    'mediamachine': {'user': 'root', 'sudo': '', },
    'mediamachine-rp4': {'user': 'root', 'sudo': '', },
    'octoprint': {'user': 'pi', 'sudo': 'sudo', },
    'raspberrypi': {'user': 'pi', 'sudo': 'sudo', },
    'reinski-tvh': {'user': 'pi', 'sudo': 'sudo', },
    'reinskisnips': {'user': 'pi', 'sudo': 'sudo', },
    'sarahpi': {'user': 'pi', 'sudo': 'sudo', },
#    'reinski-nas-2': {'user': 'admin', 'sudo': 'sudo', },
}

commands = {
    'check': {'cmd': 'nc -vz {host} 22', 'ok': '.*succeeded.*', 'cmdname': 'check'},
    'reboot': {'cmd': 'ssh {user}@{host} {sudo} reboot now', 'cmdname': 'reboot'},
    'shutdown': {'cmd': 'ssh {user}@{host} {sudo} shutdown now', 'cmdname': 'shutdown'},
}


def update_device_statuses():
    global devices
    for device, dev_data in devices.items():
        result = execute_command(commands['check'], device, dev_data, False)
        dev_data['check-result'] = result
    
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4999)