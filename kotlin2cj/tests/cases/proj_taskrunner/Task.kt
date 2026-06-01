data class Task(val id: Int, val name: String, val priority: Int) {
    var completed: Boolean = false

    fun complete() {
        completed = true
    }

    fun describe(): String {
        val status = if (completed) "DONE" else "TODO"
        return "[$status] #$id $name (pri=$priority)"
    }
}
