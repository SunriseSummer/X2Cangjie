package proj_petshop.service

import std.collection.*
import proj_petshop.model.*

public class PetShop {
    public let shopName: String
    public init(shopName: String) {
        this.shopName = shopName
    }
    public let pets = ArrayList<Pet>()
    public func addPet(pet: Pet) {
        pets.add(pet)
        println("Added ${pet.name} to ${shopName}")
    }
    public func listPets() {
        println("Pets in ${shopName}:")
        for (pet in pets) {
            println("  - ${pet.describe()}")
        }
    }
    public func findBySpecies(species: String): ArrayList<Pet> {
        return collectArrayList(pets.iterator().filter({ it => it.species == species }))
    }
}
