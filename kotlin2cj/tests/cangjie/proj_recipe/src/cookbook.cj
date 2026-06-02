package proj_recipe

import std.collection.*

class Cookbook {
    let bookName: String
    init(bookName: String) {
        this.bookName = bookName
    }
    let recipes = ArrayList<Recipe>()
    func addRecipe(recipe: Recipe) {
        recipes.add(recipe)
    }
    func findByName(name: String): ?Recipe {
        for (r in recipes) {
            if (r.recipeName == name) {
                return r
            }
        }
        return None
    }
    func totalIngredients(): Int64 {
        var count = 0
        for (r in recipes) {
            count += r.ingredientCount()
        }
        return count
    }
    func printTableOfContents() {
        println("=== ${bookName} ===")
        println("Recipes (${recipes.size}):")
        var idx = 1
        for (r in recipes) {
            println("  ${idx}. ${r.recipeName} (serves ${r.servings}, ${r.ingredientCount()} ingredients)")
            idx += 1
        }
        println("Total unique ingredient entries: ${totalIngredients()}")
    }
    func printAll() {
        for (r in recipes) {
            r.printRecipe()
            println()
        }
    }
}
