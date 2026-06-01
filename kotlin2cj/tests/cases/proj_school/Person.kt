open class Person(val name: String, val age: Int) {
    open fun role(): String = "Person"

    fun introduce(): String {
        return "${role()}: $name, age $age"
    }
}
