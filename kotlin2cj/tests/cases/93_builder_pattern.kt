// Builder pattern with method chaining (returns this)
class QueryBuilder {
    var table = ""
    val conditions = ArrayList<String>()
    var sortField = ""
    var limitVal = -1

    fun from(t: String): QueryBuilder {
        table = t
        return this
    }

    fun where(cond: String): QueryBuilder {
        conditions.add(cond)
        return this
    }

    fun orderBy(field: String): QueryBuilder {
        sortField = field
        return this
    }

    fun limit(n: Int): QueryBuilder {
        limitVal = n
        return this
    }

    fun build(): String {
        var sql = "SELECT * FROM $table"
        if (conditions.isNotEmpty()) {
            sql += " WHERE " + conditions.joinToString(" AND ")
        }
        if (sortField.isNotEmpty()) {
            sql += " ORDER BY $sortField"
        }
        if (limitVal > 0) {
            sql += " LIMIT $limitVal"
        }
        return sql
    }
}

fun main() {
    val q1 = QueryBuilder()
        .from("users")
        .where("age > 18")
        .where("active = true")
        .orderBy("name")
        .limit(10)
        .build()
    println(q1)

    val q2 = QueryBuilder()
        .from("orders")
        .build()
    println(q2)

    val q3 = QueryBuilder()
        .from("products")
        .where("price < 100")
        .limit(5)
        .build()
    println(q3)

    // Test multiple independent builders
    val b1 = QueryBuilder().from("a")
    val b2 = QueryBuilder().from("b")
    b1.where("x = 1")
    b2.where("y = 2")
    println(b1.build())
    println(b2.build())
}
