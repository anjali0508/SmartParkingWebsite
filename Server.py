from flask import Flask, make_response, jsonify, abort, request, render_template, url_for, redirect, session
import pyrebase
import bcrypt
import FirebaseConfig.Configure as firebase
import time
from Database.IDGenerator import ID as IDgen
IDgen = IDgen()
IDgen.setVisitorID()
IDgen.setResidentVehicleID()
IDgen.setResidentID()
IDgen.setParkingSlotID()

# Reference to firebese databse
dbRef = firebase.dbRef

app = Flask(__name__)


@app.errorhandler(404)
def notFound(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def badRequest(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route("/")
@app.route("/Login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("Login.html", login="nil")
    elif request.method == "POST":
        if not request.json or not "Username" in request.json or not "Password" in request.json:
            abort(400)
        username = request.json["Username"]
        password = request.json["Password"].encode('utf8')
        if username == "Admin":
            adminPassword = dbRef.child("Admin").get()[0].val()["Password"]
            if bcrypt.checkpw(password, adminPassword):
                session["LoggedIn"] = True
                session["User"] = username
                return jsonify({
                    "Login": "Successful",
                    "Redirect": "/Admin/Residents"
                })
        user = dbRef.child("Residents").order_by_child(
            "FlatNo").equal_to(username).get()
        try:
            userPassword = user[0].val()["Password"]
            if bcrypt.checkpw(password, userPassword):
                session["LoggedIn"] = True
                session["User"] = username
                return jsonify({
                    "Login": "Successful",
                    "Redirect": "/Resident"
                })
            else:
                return jsonify({"Login": "Failed"})
        except IndexError:
            return jsonify({"Login": "Failed"})
    else:
        abort(404)


@app.route("/Logout")
def logout():
    if session.get("LoggedIn"):
        del session["LoggedIn"]
        del session["User"]
    return jsonify({"Logout": "Successful"})


@app.route("/Resident/Profile", methods=["GET"])
def profile():
    if not session.get("LoggedIn") or session.get("User") == "Admin":
        return render_template("Login.html", login="nil")

    id = session.get("User")
    residentDetails = dbRef.child("Residents").order_by_child(
        "FlatNo").equal_to(id).get()

    details = residentDetails[0].val()
    return render_template("ResidentProfile.html", details=details)


@app.route("/Resident/", methods=["GET"])
def home():
    if not session.get("LoggedIn") or session.get("User") == "Admin":
        return render_template("Login.html", login="nil")

    id = session.get("User")
    # Get vehicle details
    vehicles = []
    vehicleDetails = dbRef.child("ResidentVehicles").order_by_child(
        "FlatNo").equal_to(id).get()
    for vehicle in vehicleDetails:
        details = vehicle.val()
        del details["FlatNo"]
        vehicles.append(details)
    # Get visitor details
    visitors = []
    visitorDetails = dbRef.child("Visitors").order_by_child(
        "FlatNo").equal_to(id).get()
    for visitor in visitorDetails:
        details = visitor.val()
        del details["FlatNo"]
        visitors.append(details)
    return render_template(
        "ResidentHome.html",
        vehicles=vehicles,
        vehicleCount=len(vehicles),
        visitorVehicles=visitors,
        visitorCount=len(visitors)
    )


@app.route("/Resident/Visitor", methods=["POST", "DELETE"])
def visitorFunctions():
    if not session.get("LoggedIn") or session.get("User") == "Admin":
        return render_template("Login.html", login="nil")

    id = session.get("User")
    flatNo = session.get("User")
    if request.method == "POST":
        if not request.json or not "VehicleNo" in request.json:
            abort(400)
        visitor = {
            "AllottedSlot": "",
            "Arrived": False,
            "Departed": False,
            "FlatNo": id,
            "Name": request.json.get("Name", ""),
            "VehicleNo": request.json["VehicleNo"]
        }

        visitorID = IDgen.getNextVisitorID()
        dbRef.child("Visitors").child(visitorID).set(visitor)
        return jsonify({"Success": True})

    if request.method == "DELETE":
        if not request.json or not "VehicleNo" in request.json:
            abort(400)
        vehicleNo = request.json["VehicleNo"]
        details = dbRef.child("Visitors").order_by_child(
            "VehicleNo").equal_to(vehicleNo).get()
        try:
            visitorID = details[0].key()
            flatNo = details[0].val()["FlatNo"]
            if flatNo == id:
                dbRef.child("Visitors").child(visitorID).remove()
                return jsonify({"Success": True})
            else:
                return jsonify({"Success": False, "Message": "Invalid Vehicle Number"})
        except IndexError:
            return jsonify({"Success": False, "Message": "Invalid Vehicle Number"})
        

@app.route("/Resident/ChangePassword", methods=["PATCH"])
def changePassword():
    if not session.get("LoggedIn") or session.get("User") == "Admin":
        return render_template("Login.html", login="nil")
    id = session.get("User")
    if not request.json or not "CurrentPassword" in request.json or not "NewPassword" in request.json:
        abort(400)
    # Hash later
    currentPassword = request.json["CurrentPassword"].encode('utf8')
    newPassword = request.json["NewPassword"].encode('utf8')
    newPassword = bcrpyt.hashpw(newPassword, bcrpyt.gensalt())
    details = dbRef.child("Residents").order_by_child(
        "FlatNo").equal_to(id).get()
    userID = details[0].key()
    password = details[0].val()["Password"]
    if bcrpyt.checkpw(currentPassword, password):
        dbRef.child("Residents").child(userID).update({"Password": newPassword})
        return jsonify({"Success": True, "Message": "Password change successful!"})
    else:
        return jsonify({"Success": False, "Message": "Current Password you entered is wrong"})


@app.route("/Admin/Residents", methods=["GET", "PUT", "DELETE", "POST"])
def residentFuctions():
    if not session.get("User") == "Admin":
        return render_template("Login.html", login="nil")
    if request.method == "GET":
        residents = dbRef.child("Residents").get()
        details = [resident.val()
                   for resident in residents if resident.val() != None]
        # return jsonify({"Residents": details, "residentCount": len(details)}, 200)
        return render_template(
            "Admin_Residents.html",
            Residents=details,
            residentCount=len(details)
        )

    elif request.method == "POST":
        if not request.json or not "FlatNo" in request.json or not "Password" in request.json:
            print("lala")
            abort(400)
        password = request.json["Password"].encode('utf8')
        password = bcrypt.hashpw(password, bcrypt.gensalt())
        resident = {
            "Email": request.json.get("Email", ""),
            "FlatNo": request.json["FlatNo"],
            "Name": request.json.get("Name", ""),
            "Password": password,
            "PhoneNo": request.json.get("PhoneNo", "")
        }
        residentID = IDgen.getNextResidentID()
        dbRef.child("Residents").child(residentID).set(resident)
        return jsonify({"Success": True})

    elif request.method == "PUT":
        if not request.json or not "FlatNo" in request.json:
            abort(400)
        resident = {}
        flatNo = request.json["FlatNo"]
        if "Name" in request.json:
            resident["Name"] = request.json["Name"]
        if "Email" in request.json:
            resident["Email"] = request.json["Email"]
        if "Password" in request.json:
            resident["Password"] = request.json["Password"]
        if "PhoneNo" in request.json:
            resident["PhoneNo"] = request.json["PhoneNo"]
        details = dbRef.child("Residents").order_by_child(
            "FlatNo").equal_to(flatNo).get()
        try:
            ID = details[0].key()
            dbRef.child("Residents").child(ID).update(resident)
            return jsonify({"Success": True})
        except:
            return jsonify({"Success": False, "Message": "Flat Number does not exist"})

    elif request.method == "DELETE":
        if not request.json or not "FlatNo" in request.json:
            abort(400)
        flatNo = request.json["FlatNo"]
        details = dbRef.child("Residents").order_by_child(
            "FlatNo").equal_to(flatNo).get()
        try:
            ID = details[0].key()
            if ID == None:
                return jsonify({"Success": False, "Message": "Flat Number does not exist"})
            # Remove visitors 
            visitors = dbRef.child("Visitors").order_by_child("FlatNo").equal_to(flatNo).get()
            for visitor in visitors:
                visitorDetails = visitor.val()
                if visitorDetails["Arrived"] == False:
                    key = visitor.key()
                    dbRef.child("Visitors").child(key).remove()
                else:
                    return jsonify({"Success": False, "Message": "Cannot delete resident, Visitor vehicle present"})
            # Remove vehicles 
            vehicles = dbRef.child("ResidentVehicles").order_by_child("FlatNo").equal_to(flatNo).get()
            for vehicle in vehicles:
                key = vehicle.key()
                dbRef.child("ResidentVehivles").child(key).remove()
            # Remove the resident 
            dbRef.child("Residents").child(ID).remove()
            return jsonify({"Success": True})
        except IndexError:
            return jsonify({"Success": False, "Message": "Flat Number does not exist"})
    else:
        abort(404)


@app.route("/Admin/ResidentVehicles", methods=["GET", "DELETE", "POST"])
def residentVehicleFuctions():
    if not session.get("User") == "Admin":
        return render_template("Login.html", login="nil")
    if request.method == "GET":
        vehicles = dbRef.child(
            "ResidentVehicles").get()
        details = [vehicles.val()
                   for vehicles in vehicles if vehicles.val() != None]
        # return jsonify({"Vehicles": details, "VehicleCount": len(details)}, 200)
        return render_template(
            "Admin_ResidentVehicles.html",
            vehicles=details,
            vehicleCount=len(details)
        )

    elif request.method == "POST":
        if (
            not request.json or
            not "FlatNo" in request.json or
            not "VehicleNo" in request.json or
            not "AllottedSlot" in request.json
        ):
            abort(400)

        slot = request.json["AllottedSlot"]
        slotDetails = dbRef.child("ParkingSlots").order_by_child(
            "SlotNo").equal_to(slot).get()
        try:
            if slotDetails[0].val()["Allotted"] == False:
                key = slotDetails[0].key()
                # Update slot details
                dbRef.child("ParkingSlots").child(
                    key).update({"Allotted": True})
                # Add vehicle
                vehicle = {
                    "FlatNo": request.json["FlatNo"],
                    "VehicleNo": request.json["VehicleNo"],
                    "AllottedSlot": request.json["AllottedSlot"]
                }
                vehicleID = IDgen.getNextResidentVehicleID()
                dbRef.child("ResidentVehicles").child(
                    vehicleID).set(vehicle)
                return jsonify({"Success": True})
            else:
                return jsonify({"Success": False, "Message": "The requested slot is not free"})
        except IndexError:
            return jsonify({"Success": False, "Message": "The requested slot is not available"})

    elif request.method == "DELETE":
        if not request.json or not "VehicleNo" in request.json:
            abort(400)
        vehicleNo = request.json["VehicleNo"]
        details = dbRef.child("ResidentVehicles").order_by_child(
            "VehicleNo").equal_to(vehicleNo).get()

        try:
            ID = details[0].key()
            if ID == None:
                return jsonify({"Success": False, "Message": "The vehicle does not exist"})
            slot = details[0].val()["AllottedSlot"]
            # Free the allotted slot
            slotDetails = dbRef.child("ParkingSlots").order_by_child(
                "SlotNo").equal_to(slot).get()
            key = slotDetails[0].key()
            dbRef.child("ParkingSlots").child(key).update({"Allotted": False})
            dbRef.child("ResidentVehicles").child(ID).remove()
            return jsonify({"Success": True})
        except IndexError:
            return jsonify({"Success": False, "Message": "The vehicle does not exist"})

    else:
        abort(404)


if __name__ == '__main__':
    app.secret_key = "SecretKEY"
    app.run(debug=True, port=4000)
