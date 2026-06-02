data class Transaction(val memberId: Int, val bookIsbn: String, val action: String) {
    fun describe(): String = "$action: member=$memberId, book=$bookIsbn"
}
