package proj_hospital

import std.collection.*

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
