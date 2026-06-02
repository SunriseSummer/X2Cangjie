class Pet(val name: String, val species: String, val age: Int) {
    fun describe(): String {
        return "$name is a $species, $age year(s) old"
    }
}
