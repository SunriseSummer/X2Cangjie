package proj_hospital

import std.collection.*

class Doctor <: Person {
    let specialty: String
    init(name: String, age: Int64, specialty: String) {
        super(name, age)
        this.specialty = specialty
    }
    let patients = ArrayList<Patient>()
    public override func role(): String {
        return "Doctor"
    }
    func addPatient(patient: Patient) {
        patients.add(patient)
    }
    func removePatient(patient: Patient) {
        for (i in 0..patients.size) {
            if (patients[i].patientId == patient.patientId) {
                patients.remove(at: i)
                break
            }
        }
    }
    func patientCount(): Int64 {
        return patients.size
    }
    func printPatients() {
        println("Dr. ${name} (${specialty}) - ${patientCount()} patients:")
        for (p in patients) {
            println("    - ${p.name} (#${p.patientId})")
        }
    }
}

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

class Patient <: Person {
    let patientId: Int64
    init(name: String, age: Int64, patientId: Int64) {
        super(name, age)
        this.patientId = patientId
    }
    let diagnoses = ArrayList<String>()
    var admitted: Bool = false
    var doctorName: String = "none"
    public override func role(): String {
        return "Patient"
    }
    func addDiagnosis(diagnosis: String) {
        diagnoses.add(diagnosis)
    }
    func admit(doctor: Doctor) {
        admitted = true
        doctorName = doctor.name
        doctor.addPatient(this)
    }
    func discharge(doctor: Doctor) {
        admitted = false
        doctor.removePatient(this)
        doctorName = "none"
    }
    func printRecord() {
        let status = if (admitted) {
            "admitted"
        } else {
            "discharged"
        }
        println("  Patient #${patientId}: ${name} (${status}, doctor: ${doctorName})")
        if (!(diagnoses.isEmpty())) {
            println("    Diagnoses: ${diagnoses.size}")
            for (d in diagnoses) {
                println("      - ${d}")
            }
        }
    }
}

open class Person {
    let name: String
    let age: Int64
    init(name: String, age: Int64) {
        this.name = name
        this.age = age
    }
    public open func role(): String {
        return "Person"
    }
    public open func info(): String {
        return "${role()}: ${name}, age ${age}"
    }
}

main() {
    let hospital = Hospital("General Hospital")
    hospital.addDoctor(Doctor("Smith", 45, "Cardiology"))
    hospital.addDoctor(Doctor("Jones", 38, "Neurology"))
    hospital.addDoctor(Doctor("Lee", 52, "Orthopedics"))
    println()
    let p1 = hospital.admitPatient("Alice", 30, "Smith")
    let p2 = hospital.admitPatient("Bob", 45, "Smith")
    let p3 = hospital.admitPatient("Charlie", 60, "Jones")
    let p4 = hospital.admitPatient("Diana", 25, "Lee")
    if (let Some(p1) <- p1) {
        p1.addDiagnosis("Hypertension")
        p1.addDiagnosis("Arrhythmia")
    }
    if (let Some(p3) <- p3) {
        p3.addDiagnosis("Migraine")
    }
    println()
    hospital.printStatus()
    println()
    println("Discharging Alice...")
    if (let Some(p1) <- p1) {
        hospital.dischargePatient(p1.patientId)
    }
    println()
    hospital.printStatus()
    println()
    hospital.printAllRecords()
    println()
    println("Patient details:")
    if (let Some(p1) <- p1) {
        p1.printRecord()
    }
    if (let Some(p2) <- p2) {
        p2.printRecord()
    }
    if (let Some(p3) <- p3) {
        p3.printRecord()
    }
    if (let Some(p4) <- p4) {
        p4.printRecord()
    }
}