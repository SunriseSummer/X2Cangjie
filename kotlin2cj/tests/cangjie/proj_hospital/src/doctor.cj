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
