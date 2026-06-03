import model.Pet
import service.PetShop

fun main() {
    val shop = PetShop("Happy Paws")
    shop.addPet(Pet("Buddy", "Dog", 3))
    shop.addPet(Pet("Whiskers", "Cat", 2))
    shop.addPet(Pet("Goldie", "Fish", 1))
    shop.addPet(Pet("Rex", "Dog", 5))
    shop.listPets()

    val dogs = shop.findBySpecies("Dog")
    println("Dogs found: ${dogs.size}")
    for (dog in dogs) {
        println("  ${dog.name}")
    }
}
