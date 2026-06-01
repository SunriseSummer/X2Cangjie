data class Book(val isbn: String, val title: String, val author: String, val year: Int) {
    var available: Boolean = true

    fun info(): String {
        val status = if (available) "available" else "checked out"
        return "$title by $author ($year) [$status]"
    }
}
