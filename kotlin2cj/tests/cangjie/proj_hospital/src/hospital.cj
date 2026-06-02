package proj_hospital

import std.collection.*

class MedicalRecord <: ToString {
    let patientId: Int64
    let doctorName: String
    let action: String
    init(patientId: Int64, doctorName: String, action: String) {
        this.patientId = patientId
        this.doctorName = doctorName
        this.action = action
    }
    public func toString(): String {
        return "MedicalRecord(patientId=${this.patientId}, doctorName=${this.doctorName}, action=${this.action})"
    }
}

class Hospital {
    let hospitalName: String
    init(hospitalName: String) {
        this.hospitalName = hospitalName
    }
    let doctors = ArrayList<Doctor>()
    let allPatients = ArrayList<Patient>()
    let records = ArrayList<MedicalRecord>()
    var nextPatientId = 1
    func addDoctor(doctor: Doctor) {
        doctors.add(doctor)
        println("Dr. ${doctor.name} (${doctor.specialty}) joined ${hospitalName}")
    }
    func admitPatient(patientName: String, age: Int64, doctorName: String): ?Patient {
        var foundDoc: ?Doctor = None
        for (d in doctors) {
            if (d.name == doctorName) {
                foundDoc = d
                break
            }
        }
        let doc = foundDoc ?? return
        None
        let patient = Patient(patientName, age, nextPatientId)
        nextPatientId += 1
        allPatients.add(patient)
        patient.admit(doc)
        records.add(MedicalRecord(patient.patientId, doctorName, "ADMIT"))
        println("Admitted ${patient.name} (#${patient.patientId}) under Dr. ${doctorName}")
        return patient
    }
    func dischargePatient(patientId: Int64) {
        for (p in allPatients) {
            if ((p.patientId == patientId) && p.admitted) {
                let docName = p.doctorName
                for (d in doctors) {
                    if (d.name == docName) {
                        p.discharge(d)
                        break
                    }
                }
                records.add(MedicalRecord(patientId, docName, "DISCHARGE"))
                println("Discharged ${p.name} (#${patientId})")
                return
            }
        }
        println("Patient #${patientId} not found or already discharged")
    }
    func admittedCount(): Int64 {
        var count = 0
        for (p in allPatients) {
            if (p.admitted) {
                count += 1
            }
        }
        return count
    }
    func printStatus() {
        println("=== ${hospitalName} Status ===")
        println("Doctors: ${doctors.size}")
        println("Admitted patients: ${admittedCount()}")
        println("Total records: ${records.size}")
        for (d in doctors) {
            d.printPatients()
        }
    }
    func printAllRecords() {
        println("=== Medical Records ===")
        for (r in records) {
            println("  Patient #${r.patientId}: ${r.action} by Dr. ${r.doctorName}")
        }
    }
}
