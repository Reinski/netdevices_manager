from flask import redirect, request, render_template, url_for
from datetime import datetime
from . import app
from . import webapp

@app.route('/')
def home():
    return redirect(url_for('list_devices'), code=302)


@app.route("/manage/<name>")
@app.route("/manage/")
@app.route("/manage")
def manage_device(name = None):
    return render_template("manage_device.html",
                            name=name,
                            date=datetime.now()
                            )

@app.route("/list_devices", methods=["GET", "POST"])
@app.route("/list_devices/", methods=["GET", "POST"])
def list_devices():
    now = datetime.now()
    msgtxt = None
    args = request.args.to_dict(flat=False)
    if len(args) > 0:
        # process the command
        action = args.get('action', None)
        if action:
            action = action[0]
            sel_devices = args.get('device', [])
            if len(sel_devices) == 0:
                msgtxt = "No devices selected!"
            else:
                msgtxt = webapp.process_devices(action, sel_devices)
        return redirect(url_for('list_devices'), code=302)
    else:
        # Update and display device list
        webapp.update_device_statuses()
        return render_template("bootstrap_devicelist.html", title = webapp.title, host_rows = webapp.devices, message = msgtxt)
