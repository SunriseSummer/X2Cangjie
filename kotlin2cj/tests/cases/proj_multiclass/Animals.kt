open class Animal(val name: String, val legs: Int) {
    open fun speak(): String = "$name says nothing"
    fun describe(): String = "$name has $legs legs"
}

class Dog(name: String) : Animal(name, 4) {
    override fun speak(): String = "$name says Woof!"
}

class Cat(name: String) : Animal(name, 4) {
    override fun speak(): String = "$name says Meow!"
}

class Bird(name: String) : Animal(name, 2) {
    override fun speak(): String = "$name says Tweet!"
    fun canFly(): Boolean = true
}

class Fish(name: String) : Animal(name, 0) {
    override fun speak(): String = "$name says Blub!"
    fun canSwim(): Boolean = true
}
