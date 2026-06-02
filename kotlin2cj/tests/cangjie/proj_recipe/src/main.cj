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

class Ingredient <: ToString {
    let name: String
    let amount: Int64
    let unit: String
    init(name: String, amount: Int64, unit: String) {
        this.name = name
        this.amount = amount
        this.unit = unit
    }
    func describe(): String {
        return "${amount} ${unit} ${name}"
    }
    func scale(factor: Int64): Ingredient {
        return Ingredient(name, amount * factor, unit)
    }
    public func toString(): String {
        return "Ingredient(name=${this.name}, amount=${this.amount}, unit=${this.unit})"
    }
}

class Recipe {
    let recipeName: String
    let servings: Int64
    init(recipeName: String, servings: Int64) {
        this.recipeName = recipeName
        this.servings = servings
    }
    let ingredients = ArrayList<Ingredient>()
    let steps = ArrayList<String>()
    func addIngredient(ingredient: Ingredient) {
        ingredients.add(ingredient)
    }
    func addStep(step: String) {
        steps.add(step)
    }
    func scaleFor(newServings: Int64): Recipe {
        let factor = newServings / servings
        let scaled = Recipe(recipeName, newServings)
        for (ing in ingredients) {
            scaled.addIngredient(ing.scale(factor))
        }
        for (step in steps) {
            scaled.addStep(step)
        }
        return scaled
    }
    func printRecipe() {
        println("--- ${recipeName} (serves ${servings}) ---")
        println("Ingredients:")
        for (ing in ingredients) {
            println("  ${ing.describe()}")
        }
        println("Steps:")
        var num = 1
        for (step in steps) {
            println("  ${num}. ${step}")
            num += 1
        }
    }
    func ingredientCount(): Int64 {
        return ingredients.size
    }
}

main() {
    let book = Cookbook("Family Favorites")
    let pasta = Recipe("Pasta", 4)
    pasta.addIngredient(Ingredient("spaghetti", 400, "g"))
    pasta.addIngredient(Ingredient("tomato sauce", 200, "ml"))
    pasta.addIngredient(Ingredient("garlic", 3, "cloves"))
    pasta.addIngredient(Ingredient("olive oil", 2, "tbsp"))
    pasta.addStep("Boil water and cook spaghetti")
    pasta.addStep("Saute garlic in olive oil")
    pasta.addStep("Add tomato sauce and simmer")
    pasta.addStep("Combine and serve")
    book.addRecipe(pasta)
    let salad = Recipe("Caesar Salad", 2)
    salad.addIngredient(Ingredient("romaine lettuce", 1, "head"))
    salad.addIngredient(Ingredient("croutons", 100, "g"))
    salad.addIngredient(Ingredient("parmesan", 50, "g"))
    salad.addIngredient(Ingredient("caesar dressing", 60, "ml"))
    salad.addStep("Wash and chop lettuce")
    salad.addStep("Add croutons and parmesan")
    salad.addStep("Drizzle with dressing and toss")
    book.addRecipe(salad)
    let soup = Recipe("Tomato Soup", 6)
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
    let pastaFor8 = pasta.scaleFor(8)
    println("Scaled recipe:")
    pastaFor8.printRecipe()
    let found = book.findByName("Caesar Salad")
    if (let Some(found) <- found) {
        println()
        println("Found: ${found.recipeName} with ${found.ingredientCount()} ingredients")
    }
}