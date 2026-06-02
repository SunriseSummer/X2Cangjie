class Cookbook(val bookName: String) {
    val recipes = mutableListOf<Recipe>()

    fun addRecipe(recipe: Recipe) {
        recipes.add(recipe)
    }

    fun findByName(name: String): Recipe? {
        for (r in recipes) {
            if (r.recipeName == name) return r
        }
        return null
    }

    fun totalIngredients(): Int {
        var count = 0
        for (r in recipes) {
            count += r.ingredientCount()
        }
        return count
    }

    fun printTableOfContents() {
        println("=== $bookName ===")
        println("Recipes (${recipes.size}):")
        var idx = 1
        for (r in recipes) {
            println("  $idx. ${r.recipeName} (serves ${r.servings}, ${r.ingredientCount()} ingredients)")
            idx++
        }
        println("Total unique ingredient entries: ${totalIngredients()}")
    }

    fun printAll() {
        for (r in recipes) {
            r.printRecipe()
            println()
        }
    }
}
