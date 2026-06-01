import std.collection.*

class QueryBuilder {
    var table = ""
    let conditions = ArrayList<String>()
    var sortField = ""
    var limitVal = -1
    func from(t: String): QueryBuilder {
        table = t
        return this
    }
    func `where`(cond: String): QueryBuilder {
        conditions.add(cond)
        return this
    }
    func orderBy(field: String): QueryBuilder {
        sortField = field
        return this
    }
    func limit(n: Int64): QueryBuilder {
        limitVal = n
        return this
    }
    func build(): String {
        var sql = "SELECT * FROM ${table}"
        if (!(conditions.isEmpty())) {
            sql += " WHERE " + String.join(collectArray<String>(conditions.iterator().map({e => e.toString()})), delimiter: " AND ")
        }
        if (!(sortField.isEmpty())) {
            sql += " ORDER BY ${sortField}"
        }
        if (limitVal > 0) {
            sql += " LIMIT ${limitVal}"
        }
        return sql
    }
}

main() {
    let q1 = QueryBuilder().from("users").`where`("age > 18").`where`("active = true").orderBy("name").limit(10).build()
    println(q1)
    let q2 = QueryBuilder().from("orders").build()
    println(q2)
    let q3 = QueryBuilder().from("products").`where`("price < 100").limit(5).build()
    println(q3)
    let b1 = QueryBuilder().from("a")
    let b2 = QueryBuilder().from("b")
    b1.`where`("x = 1")
    b2.`where`("y = 2")
    println(b1.build())
    println(b2.build())
}
