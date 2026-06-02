fun main() {
    val hospital = Hospital("General Hospital")

    hospital.addDoctor(Doctor("Smith", 45, "Cardiology"))
    hospital.addDoctor(Doctor("Jones", 38, "Neurology"))
    hospital.addDoctor(Doctor("Lee", 52, "Orthopedics"))

    println()
    val p1 = hospital.admitPatient("Alice", 30, "Smith")
    val p2 = hospital.admitPatient("Bob", 45, "Smith")
    val p3 = hospital.admitPatient("Charlie", 60, "Jones")
    val p4 = hospital.admitPatient("Diana", 25, "Lee")

    if (p1 != null) {
        p1.addDiagnosis("Hypertension")
        p1.addDiagnosis("Arrhythmia")
    }
    if (p3 != null) {
        p3.addDiagnosis("Migraine")
    }

    println()
    hospital.printStatus()

    println()
    println("Discharging Alice...")
    if (p1 != null) {
        hospital.dischargePatient(p1.patientId)
    }

    println()
    hospital.printStatus()

    println()
    hospital.printAllRecords()

    println()
    println("Patient details:")
    if (p1 != null) p1.printRecord()
    if (p2 != null) p2.printRecord()
    if (p3 != null) p3.printRecord()
    if (p4 != null) p4.printRecord()
}
