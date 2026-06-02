package proj_school

import std.collection.*

open class Person {
    let name: String
    let age: Int64
    init(name: String, age: Int64) {
        this.name = name
        this.age = age
    }
    public open func role(): String {
        return "Person"
    }
    public open func introduce(): String {
        return "${role()}: ${name}, age ${age}"
    }
}
