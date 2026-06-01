class Doctor(name: String, age: Int, val specialty: String) : Person(name, age) {
    val patients = mutableListOf<Patient>()

    override fun role(): String = "Doctor"

    fun addPatient(patient: Patient) {
        patients.add(patient)
    }

    fun removePatient(patient: Patient) {
        for (i in 0 until patients.size) {
            if (patients[i].patientId == patient.patientId) {
                patients.removeAt(i)
                break
            }
        }
    }

    fun patientCount(): Int = patients.size

    fun printPatients() {
        println("Dr. $name ($specialty) - ${patientCount()} patients:")
        for (p in patients) {
            println("    - ${p.name} (#${p.patientId})")
        }
    }
}
