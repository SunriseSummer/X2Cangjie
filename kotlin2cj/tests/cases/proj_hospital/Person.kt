open class Person(val name: String, val age: Int) {
    open fun role(): String = "Person"
    fun info(): String = "${role()}: $name, age $age"
}
