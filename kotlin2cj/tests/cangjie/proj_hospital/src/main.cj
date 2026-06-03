package proj_hospital

import std.collection.*

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
