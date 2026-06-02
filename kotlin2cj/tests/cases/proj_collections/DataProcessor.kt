package proj_collections

class DataProcessor(val data: List<Int>) {
    fun doubleAll(): List<Int> = data.map { it * 2 }
    fun onlyPositive(): List<Int> = data.filter { it > 0 }
    fun removeNegative(): List<Int> = data.filterNot { it < 0 }
    fun withIndices(): List<Int> = data.mapIndexed { i, v -> i * 10 + v }
    fun total(): Int = data.sum()
    fun productReduce(): Int = data.reduce { a, b -> a * b }
}
