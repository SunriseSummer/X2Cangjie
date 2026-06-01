data class TournPlayer(val name: String, val skill: Int) {
    var wins: Int = 0
    var losses: Int = 0

    fun record(): String = "$wins-$losses"
    fun describe(): String = "$name (skill=$skill, record=${record()})"
}
