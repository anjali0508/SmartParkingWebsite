from firebase import firebase
firebase = firebase.FirebaseApplication(
    'https://smartparkingsystem-bca72.firebaseio.com/', None)


class ID:
    def __init__(self):
        self.residentID = 0
        self.visitorID = 0
        self.residentVehicleID = 0
        self.parkingSlotID = 0

    def setResidentID(self):
        ID = firebase.get("/ID", "ResidentID")
        if ID == None:
            firebase.put("ID", "ResidentID", {"Count": 0})
            self.residentID = 0
        else:
            self.residentID = ID["Count"]

    def getResidentID(self):
        return self.residentID

    def getNextResidentID(self):
        self.residentID += 1
        firebase.put("ID", "ResidentID", {"Count": self.residentID})
        return self.residentID

    def setVisitorID(self):
        ID = firebase.get("/ID", "VisitorID")
        if ID == None:
            firebase.put("ID", "VisitorID", {"Count": 0})
            self.visitorID = 0
        else:
            self.visitorID = ID["Count"]

    def getVisitorID(self):
        return self.visitorID

    def getNextVisitorID(self):
        self.visitorID += 1
        firebase.put("ID", "VisitorID", {"Count": self.visitorID})
        return self.visitorID

    def setResidentVehicleID(self):
        ID = firebase.get("/ID", "ResidentVehicleID")
        if ID == None:
            firebase.put("ID", "ResidentVehicleID", {"Count": 0})
            self.residentVehicleID = 0
        else:
            self.residentVehicleID = ID["Count"]

    def getResidentVehicleID(self):
        return self.residentVehicleID

    def getNextResidentVehicleID(self):
        self.residentVehicleID += 1
        firebase.put("ID", "ResidentVehicleID", {
                     "Count": self.residentVehicleID})
        return self.residentVehicleID

    def setParkingSlotID(self):
        ID = firebase.get("/ID", "ParkingSlotID")
        if ID == None:
            firebase.put("ID", "ParkingSlotID", {"Count": 0})
            self.parkingSlotID = 0
        else:
            self.parkingSlotID = ID["Count"]

    def getParkingSlotID(self):
        return self.parkingSlotID

    def getNextParkingSlotID(self):
        self.parkingSlotID += 1
        firebase.put("ID", "ParkingSlotID", {"Count": self.parkingSlotID})
        return self.parkingSlotID


if __name__ == "__main__":
    id = ID()
    id.setResidentID()
    print("Initial Resident ID:", id.getResidentID())
    print("Next Resident ID:", id.getNextResidentID())
    id.setVisitorID()
    print("Initial Visitor ID:", id.getVisitorID())
    print("Next Visitor ID:", id.getNextVisitorID())
    id.setResidentVehicleID()
    print("Initial Resident Vehicle ID:", id.getResidentVehicleID())
    print("Next Resident Vehicle ID:", id.getNextResidentVehicleID())
    id.setVisitorID()
    print("Initial Parking Slot ID:", id.getParkingSlotID())
    print("Next Parking Slot ID:", id.getNextParkingSlotID())
