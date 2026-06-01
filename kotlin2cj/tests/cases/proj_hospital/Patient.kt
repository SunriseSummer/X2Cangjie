class Patient(name: String, age: Int, val patientId: Int) : Person(name, age) {
    val diagnoses = mutableListOf<String>()
    var admitted: Boolean = false
    var doctorName: String = "none"

    override fun role(): String = "Patient"

    fun addDiagnosis(diagnosis: String) {
        diagnoses.add(diagnosis)
    }

    fun admit(doctor: Doctor) {
        admitted = true
        doctorName = doctor.name
        doctor.addPatient(this)
    }

    fun discharge(doctor: Doctor) {
        admitted = false
        doctor.removePatient(this)
        doctorName = "none"
    }

    fun printRecord() {
        val status = if (admitted) "admitted" else "discharged"
        println("  Patient #$patientId: $name ($status, doctor: $doctorName)")
        if (diagnoses.isNotEmpty()) {
            println("    Diagnoses: ${diagnoses.size}")
            for (d in diagnoses) {
                println("      - $d")
            }
        }
    }
}
