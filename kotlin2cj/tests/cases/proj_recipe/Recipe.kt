class Recipe(val recipeName: String, val servings: Int) {
    val ingredients = mutableListOf<Ingredient>()
    val steps = mutableListOf<String>()

    fun addIngredient(ingredient: Ingredient) {
        ingredients.add(ingredient)
    }

    fun addStep(step: String) {
        steps.add(step)
    }

    fun scaleFor(newServings: Int): Recipe {
        val factor = newServings / servings
        val scaled = Recipe(recipeName, newServings)
        for (ing in ingredients) {
            scaled.addIngredient(ing.scale(factor))
        }
        for (step in steps) {
            scaled.addStep(step)
        }
        return scaled
    }

    fun printRecipe() {
        println("--- $recipeName (serves $servings) ---")
        println("Ingredients:")
        for (ing in ingredients) {
            println("  ${ing.describe()}")
        }
        println("Steps:")
        var num = 1
        for (step in steps) {
            println("  $num. $step")
            num++
        }
    }

    fun ingredientCount(): Int = ingredients.size
}
