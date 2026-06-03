package proj_petshop.model

import std.collection.*

public class Pet {
    public let name: String
    public let species: String
    public let age: Int64
    public init(name: String, species: String, age: Int64) {
        this.name = name
        this.species = species
        this.age = age
    }
    public func describe(): String {
        return "${name} is a ${species}, ${age} year(s) old"
    }
}
