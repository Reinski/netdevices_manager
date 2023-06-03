# netdevice_manager
Small python webapp to manage raspberry pi (and other ssh-accessible) computers in the local network.
This project was created as a quick&dirty approach to save some time in my private environment, so it should best be considered a proof-of-concept.

## Setup
Clone the repo, adapt the config and run setup.sh.
The config must be referred to in environment variable FLASK_APP_CONFIG, so if not using the standard setup, adapt the run file accordingly.
To start manually in the background, do something like this:
```
$ cd repositories/netdevices_manager/
$ nohup ./run &
```

## Security notes
This solution uses the flask webserver which is not intended for production use. Please do not expect any stability or security!
As password access is not implemented, the public key must be added to each target's authorized keys.
Also, the hostkeys must be known to the web-server and trusted without prompting for confirmation.
This means, you must be able to do ```ssh user_name@device_address``` from the applications environment without being prompted for any additional information.

## Configuration
### Title
Under the `title:` key, you can maintain a custom title for the device overview page.
### Devices
Maintain the devices in your network in the config.yml file under the `devices:` key.

The structure for each device is:
```
{device_address}:  
  user: {user_name}  
  sudo: {sudo_command}  
```

With the following meanings:
- {device_address}  
  Hostname or IP of the device, used for establishing the connection.
- {user_name}  
  The user name used for ssh connection.
- {sudo_command}  
  The command used in case root access is required for a command (e.g. for shutdown).
  If the user is already root, then the command can be left empty, otherwise it should simply contain 'sudo'.


