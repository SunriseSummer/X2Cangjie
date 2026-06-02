class PetShop(val shopName: String) {
    val pets = mutableListOf<Pet>()

    fun addPet(pet: Pet) {
        pets.add(pet)
        println("Added ${pet.name} to $shopName")
    }

    fun listPets() {
        println("Pets in $shopName:")
        for (pet in pets) {
            println("  - ${pet.describe()}")
        }
    }

    fun findBySpecies(species: String): List<Pet> {
        return pets.filter { it.species == species }
    }
}
