from flask import Flask, flash,render_template, request, session, redirect, url_for
import datetime
import hashlib
from session22C import MongoDBHelper
from bson import ObjectId  # Import ObjectId from bson

web_app = Flask("SMART HOME AUTOMATION SYSTEM")
db_helper = MongoDBHelper()

@web_app.route("/")  # Decorator
def index():
    return render_template("login(project).html")

@web_app.route("/register(project)")
def register():
    return render_template("register(project).html")

@web_app.route("/logout(project)")
def logout():
    # Reset the Data in Session Object
    session.clear()
    return redirect("/")

@web_app.route("/add-user", methods=["POST"])
def add_user_in_db():
    # Create a Dictionary with Data from HTML Register Form
    user_data = {
        "name": request.form["name"],
        "username": request.form["username"],
        "password": hashlib.sha256(request.form["password"].encode('utf-8')).hexdigest()
    }

    db_helper.collection = db_helper.db["appuser"]
    # Save user in DataBase i.e. MongoDB
    result = db_helper.insert(user_data)

    # Write the data in the Session Object
    session['name'] = user_data["name"]
    session['username'] = user_data["username"]

    return render_template("home(project).html", name=session['name'], username=session['username'])

@web_app.route("/fetch-user", methods=["POST"])
def fetch_user_from_db():
    # Create a Dictionary with Data from HTML Login Form
    user_data = {
        "username": request.form["username"],
        "password": hashlib.sha256(request.form["password"].encode('utf-8')).hexdigest(),
    }

    db_helper.collection = db_helper.db["appuser"]
    # Fetch user in DataBase i.e. MongoDB
    result = db_helper.fetch(query=user_data)

    if len(result) > 0:
        user_data = result[0]  # Get the dictionary from List
        session['username'] = user_data["username"]
        session['name'] = user_data["name"]
        return render_template("home(project).html", name=session['name'], username=session['username'])
    else:
        return render_template("error(project).html", message="User Not Found. Please Try Again")
@web_app.route('/delete_device/<device_id>', methods=['GET'])
def delete_device(device_id):
    try:
        # Convert device_id to ObjectId
        object_id = ObjectId(device_id)

        # Perform the delete operation
        result = db_helper.delete_one({"_id": object_id})

        if result.deleted_count > 0:
            flash("Device deleted successfully!", "success")
        else:
            flash("Error: Device not found.", "danger")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")

    # Redirect back to the "Devices" page
    return redirect(url_for('view_devices'))

@web_app.route("/devices")
def view_devices():
    if 'username' in session:
        db_helper.collection = db_helper.db["devices"]
        devices = db_helper.fetch({"user_username": session['username']})
        return render_template("device.html", devices=devices, name=session['name'], username=session['username'])
    else:
        return redirect('/')

@web_app.route("/add_device", methods=["GET", "POST"])
def add_device():
    if 'username' in session:
        if request.method == "POST":
            device_data = {
                "device_name": request.form["device_name"],
                "device_type": request.form["device_type"],
                "status": request.form["status"],
                "user_username": session['username']
            }
            # Insert device data into MongoDB
            db_helper.collection = db_helper.db["devices"]
            db_helper.insert(device_data)

            # Fetch all devices again to display them as cards immediately
            devices = db_helper.fetch({"user_username": session['username']})

            return render_template("add_device.html", name=session['name'], username=session['username'], devices=devices)
        else:
            # Fetch all devices when the page is loaded (GET request)
            devices = db_helper.fetch({"user_username": session['username']})
            return render_template("add_device.html", name=session['name'], username=session['username'], devices=devices)
    else:
        return redirect('/')

@web_app.route("/control-device/<string:device_id>/<string:action>")
def control_device(device_id, action):
    if 'username' in session:
        db_helper.collection = db_helper.db["devices"]
        new_status = "On" if action == "turn_on" else "Off"
        db_helper.collection.update_one({"_id": ObjectId(device_id)}, {"$set": {"status": new_status}})
        return redirect('/devices')
    else:
        return redirect('/login(project)')

@web_app.route("/update_device/<string:device_id>", methods=["GET", "POST"])
def update_device(device_id):
    if 'username' in session:
        db_helper.collection = db_helper.db["devices"]
        device = db_helper.fetch({"_id": ObjectId(device_id), "user_username": session['username']})[0]
        if request.method == "POST":
            updated_data = {
                "device_name": request.form["device_name"],
                "device_type": request.form["device_type"],
                "status": request.form["status"]
            }
            db_helper.collection.update_one({"_id": ObjectId(device_id)}, {"$set": updated_data})
            return redirect('/devices')
        return render_template("update_device.html", device=device, name=session['name'], username=session['username'])
    else:
        return redirect('/login(project)')

@web_app.route("/select-device-update")
def select_device_update():
    if 'username' in session:
        db_helper.collection = db_helper.db["devices"]
        devices = db_helper.fetch({"user_username": session['username']})
        return render_template("select_device_update.html", devices=devices, name=session['name'], username=session['username'])
    else:
        return redirect('/')

@web_app.route("/home")
def homepage():
    return render_template("home(project).html", name=session['name'], username=session['username'])

@web_app.route("/automation_rules", methods=["GET", "POST"])
def automation_rules():
    if 'username' in session:
        db_helper.collection = db_helper.db["automation_rules"]
        if request.method == "POST":
            rule_data = {
                "rule_name": request.form["rule_name"],
                "trigger": request.form["trigger"],
                "action": request.form["action"],
                "schedule": request.form["schedule"],
                "user_username": session['username']
                
            }
            db_helper.insert(rule_data)
            return redirect('/automation_rules')

        rules = db_helper.fetch({"user_username": session['username']})
        return render_template("automation_rules.html", rules=rules, username=session['username'])
    else:
        return redirect('/login(project)')
@web_app.route("/search_device", methods=["GET", "POST"])
def search_device():
    devices = []  # Initialize devices list to display when no search is performed

    if request.method == "POST":
        try:
            # Correct query construction using 'device_name' and 'device_type' fields
            search_query = {}
            if request.form.get("device_name"):
                search_query["device_name"] = {"$regex": request.form["device_name"], "$options": "i"}  # Case-insensitive regex search
            if request.form.get("device_type"):
                search_query["device_type"] = {"$regex": request.form["device_type"], "$options": "i"}  # Case-insensitive regex search
            
            db_helper.collection = db_helper.db["devices"]  # Assuming the collection name for devices is 'devices'
            devices = db_helper.fetch(query=search_query)  # Fetching matching devices

            # Remove duplicates based on device_name (or you can use device_id if unique)
            devices = list({device["device_name"]: device for device in devices}.values())

        except Exception as e:
            return render_template("error(project).html", message=f"Error searching for devices: {str(e)}")

    return render_template("search_device.html", devices=devices)



def main():
    web_app.secret_key = "automation-app-key-v2"
    web_app.run()

if __name__ == "__main__":
    main()
