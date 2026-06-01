data class MedicalRecord(val patientId: Int, val doctorName: String, val action: String)

class Hospital(val hospitalName: String) {
    val doctors = mutableListOf<Doctor>()
    val allPatients = mutableListOf<Patient>()
    val records = mutableListOf<MedicalRecord>()
    var nextPatientId = 1

    fun addDoctor(doctor: Doctor) {
        doctors.add(doctor)
        println("Dr. ${doctor.name} (${ doctor.specialty}) joined $hospitalName")
    }

    fun admitPatient(patientName: String, age: Int, doctorName: String): Patient? {
        var foundDoc: Doctor? = null
        for (d in doctors) {
            if (d.name == doctorName) {
                foundDoc = d
                break
            }
        }
        val doc = foundDoc ?: return null
        val patient = Patient(patientName, age, nextPatientId)
        nextPatientId++
        allPatients.add(patient)
        patient.admit(doc)
        records.add(MedicalRecord(patient.patientId, doctorName, "ADMIT"))
        println("Admitted ${patient.name} (#${patient.patientId}) under Dr. $doctorName")
        return patient
    }

    fun dischargePatient(patientId: Int) {
        for (p in allPatients) {
            if (p.patientId == patientId && p.admitted) {
                val docName = p.doctorName
                // Find the doctor to properly remove patient
                for (d in doctors) {
                    if (d.name == docName) {
                        p.discharge(d)
                        break
                    }
                }
                records.add(MedicalRecord(patientId, docName, "DISCHARGE"))
                println("Discharged ${p.name} (#$patientId)")
                return
            }
        }
        println("Patient #$patientId not found or already discharged")
    }

    fun admittedCount(): Int {
        var count = 0
        for (p in allPatients) {
            if (p.admitted) count++
        }
        return count
    }

    fun printStatus() {
        println("=== $hospitalName Status ===")
        println("Doctors: ${doctors.size}")
        println("Admitted patients: ${admittedCount()}")
        println("Total records: ${records.size}")
        for (d in doctors) {
            d.printPatients()
        }
    }

    fun printAllRecords() {
        println("=== Medical Records ===")
        for (r in records) {
            println("  Patient #${r.patientId}: ${r.action} by Dr. ${r.doctorName}")
        }
    }
}
