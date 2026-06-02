package proj_recipe

import std.collection.*

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
