fun main() {
    val book = Cookbook("Family Favorites")

    val pasta = Recipe("Pasta", 4)
    pasta.addIngredient(Ingredient("spaghetti", 400, "g"))
    pasta.addIngredient(Ingredient("tomato sauce", 200, "ml"))
    pasta.addIngredient(Ingredient("garlic", 3, "cloves"))
    pasta.addIngredient(Ingredient("olive oil", 2, "tbsp"))
    pasta.addStep("Boil water and cook spaghetti")
    pasta.addStep("Saute garlic in olive oil")
    pasta.addStep("Add tomato sauce and simmer")
    pasta.addStep("Combine and serve")
    book.addRecipe(pasta)

    val salad = Recipe("Caesar Salad", 2)
    salad.addIngredient(Ingredient("romaine lettuce", 1, "head"))
    salad.addIngredient(Ingredient("croutons", 100, "g"))
    salad.addIngredient(Ingredient("parmesan", 50, "g"))
    salad.addIngredient(Ingredient("caesar dressing", 60, "ml"))
    salad.addStep("Wash and chop lettuce")
    salad.addStep("Add croutons and parmesan")
    salad.addStep("Drizzle with dressing and toss")
    book.addRecipe(salad)

    val soup = Recipe("Tomato Soup", 6)
    soup.addIngredient(Ingredient("tomatoes", 1000, "g"))
    soup.addIngredient(Ingredient("onion", 1, "large"))
    soup.addIngredient(Ingredient("cream", 100, "ml"))
    soup.addStep("Roast tomatoes and onion")
    soup.addStep("Blend until smooth")
    soup.addStep("Add cream and season")
    book.addRecipe(soup)

    book.printTableOfContents()
    println()
    book.printAll()

    // Scale a recipe
    val pastaFor8 = pasta.scaleFor(8)
    println("Scaled recipe:")
    pastaFor8.printRecipe()

    // Find recipe
    val found = book.findByName("Caesar Salad")
    if (found != null) {
        println()
        println("Found: ${found.recipeName} with ${found.ingredientCount()} ingredients")
    }
}
