// ~550-line real-world style program: HR / payroll + scheduling + reporting.
// Exercises enums, data classes, interface, abstract class, generic container,
// functional chains, nullable handling, default params, when-ranges, exceptions.

enum class Department { ENGINEERING, SALES, SUPPORT, FINANCE, HR }

enum class Role { JUNIOR, MID, SENIOR, LEAD, MANAGER }

enum class LeaveType { VACATION, SICK, PERSONAL }

data class Employee(
    val id: Int,
    val name: String,
    val dept: Department,
    val role: Role,
    val baseSalary: Int
)

data class LeaveRequest(val empId: Int, val type: LeaveType, val days: Int)

data class PayStub(val empId: Int, val gross: Int, val tax: Int, val net: Int)

// ---- interface + abstract class polymorphism ----

interface Describable {
    fun describe(): String
}

abstract class Bonus(val label: String) : Describable {
    abstract fun amount(base: Int): Int
    override fun describe(): String {
        return "$label bonus"
    }
}

class FlatBonus(label: String, val value: Int) : Bonus(label) {
    override fun amount(base: Int): Int {
        return value
    }
}

class PercentBonus(label: String, val percent: Int) : Bonus(label) {
    override fun amount(base: Int): Int {
        return base * percent / 100
    }
}

// ---- generic container ----

class Roster<T> {
    val items = ArrayList<T>()
    fun add(x: T) {
        items.add(x)
    }
    fun size(): Int {
        return items.size
    }
    fun get(i: Int): T {
        return items[i]
    }
}

// ---- role multipliers ----

fun roleMultiplier(role: Role): Int = when (role) {
    Role.JUNIOR -> 100
    Role.MID -> 120
    Role.SENIOR -> 150
    Role.LEAD -> 180
    Role.MANAGER -> 220
}

fun roleName(role: Role): String = when (role) {
    Role.JUNIOR -> "Junior"
    Role.MID -> "Mid"
    Role.SENIOR -> "Senior"
    Role.LEAD -> "Lead"
    Role.MANAGER -> "Manager"
}

fun deptName(dept: Department): String = when (dept) {
    Department.ENGINEERING -> "Engineering"
    Department.SALES -> "Sales"
    Department.SUPPORT -> "Support"
    Department.FINANCE -> "Finance"
    Department.HR -> "HR"
}

// ---- tax brackets via when-ranges ----

fun taxFor(gross: Int): Int {
    return when (gross) {
        in 0..2999 -> gross * 5 / 100
        in 3000..5999 -> gross * 10 / 100
        in 6000..9999 -> gross * 18 / 100
        else -> gross * 25 / 100
    }
}

fun effectiveSalary(emp: Employee): Int {
    return emp.baseSalary * roleMultiplier(emp.role) / 100
}

// ---- company aggregate ----

class Company(val name: String) {
    val employees = ArrayList<Employee>()
    val leaves = ArrayList<LeaveRequest>()

    fun hire(e: Employee) {
        employees.add(e)
    }

    fun requestLeave(r: LeaveRequest) {
        leaves.add(r)
    }

    fun findById(id: Int): Employee? {
        for (e in employees) {
            if (e.id == id) {
                return e
            }
        }
        return null
    }

    fun inDept(dept: Department): List<Employee> {
        val out = ArrayList<Employee>()
        for (e in employees) {
            if (e.dept == dept) {
                out.add(e)
            }
        }
        return out
    }

    fun totalPayroll(): Int {
        var total = 0
        for (e in employees) {
            total = total + effectiveSalary(e)
        }
        return total
    }

    fun leaveDaysFor(empId: Int): Int {
        var sum = 0
        for (r in leaves) {
            if (r.empId == empId) {
                sum = sum + r.days
            }
        }
        return sum
    }

    fun payStubFor(emp: Employee, bonus: Int): PayStub {
        val gross = effectiveSalary(emp) + bonus
        val tax = taxFor(gross)
        return PayStub(emp.id, gross, tax, gross - tax)
    }
}

fun pad(s: String, width: Int): String {
    var out = s
    while (out.length < width) {
        out = out + " "
    }
    return out
}

fun padNum(n: Int, width: Int): String {
    var s = n.toString()
    while (s.length < width) {
        s = " " + s
    }
    return s
}

// ---- generic priority queue (max-heap-ish, simple) ----

class MaxPicker<T>(val keyOf: (T) -> Int) {
    val items = ArrayList<T>()
    fun offer(x: T) {
        items.add(x)
    }
    fun pickTop(): T {
        var bestIdx = 0
        var bestKey = keyOf(items[0])
        for (i in 1 until items.size) {
            val k = keyOf(items[i])
            if (k > bestKey) {
                bestKey = k
                bestIdx = i
            }
        }
        return items[bestIdx]
    }
}

// ---- performance review scoring ----

data class Review(val empId: Int, val quarter: Int, val score: Int)

fun ratingLabel(avg: Int): String = when (avg) {
    in 90..100 -> "Outstanding"
    in 75..89 -> "Exceeds"
    in 60..74 -> "Meets"
    in 40..59 -> "Developing"
    else -> "Needs Improvement"
}

class ReviewBook {
    val reviews = ArrayList<Review>()
    fun record(r: Review) {
        reviews.add(r)
    }
    fun averageFor(empId: Int): Int {
        var sum = 0
        var n = 0
        for (r in reviews) {
            if (r.empId == empId) {
                sum = sum + r.score
                n = n + 1
            }
        }
        if (n == 0) {
            return 0
        }
        return sum / n
    }
    fun quartersFor(empId: Int): List<Int> {
        val out = ArrayList<Int>()
        for (r in reviews) {
            if (r.empId == empId) {
                out.add(r.quarter)
            }
        }
        return out
    }
}

// ---- histogram printing ----

fun bar(n: Int): String {
    return "#".repeat(n)
}

fun shiftCode(hour: Int): String {
    return when {
        hour < 6 -> "night"
        hour < 12 -> "morning"
        hour < 18 -> "afternoon"
        else -> "evening"
    }
}

// ---- project assignments (nested collections) ----

data class Project(val code: String, val name: String, val priority: Int)

class Portfolio {
    val projects = ArrayList<Project>()
    val assignments = HashMap<String, ArrayList<Int>>()

    fun addProject(p: Project) {
        projects.add(p)
        assignments[p.code] = ArrayList<Int>()
    }

    fun assign(code: String, empId: Int) {
        assignments[code]?.add(empId)
    }

    fun teamSize(code: String): Int {
        return assignments[code]?.size ?: 0
    }

    fun byPriority(): List<Project> {
        return projects.sortedByDescending { it.priority }
    }

    fun assignmentCount(): Int {
        var total = 0
        for (p in projects) {
            total = total + teamSize(p.code)
        }
        return total
    }
}

fun main() {
    val co = Company("Acme")
    co.hire(Employee(1, "Alice", Department.ENGINEERING, Role.SENIOR, 5000))
    co.hire(Employee(2, "Bob", Department.SALES, Role.MID, 4000))
    co.hire(Employee(3, "Carol", Department.ENGINEERING, Role.LEAD, 6000))
    co.hire(Employee(4, "Dave", Department.SUPPORT, Role.JUNIOR, 3000))
    co.hire(Employee(5, "Eve", Department.FINANCE, Role.MANAGER, 7000))
    co.hire(Employee(6, "Frank", Department.ENGINEERING, Role.JUNIOR, 3200))
    co.hire(Employee(7, "Grace", Department.SALES, Role.SENIOR, 5200))
    co.hire(Employee(8, "Heidi", Department.HR, Role.MID, 3800))

    co.requestLeave(LeaveRequest(1, LeaveType.VACATION, 5))
    co.requestLeave(LeaveRequest(1, LeaveType.SICK, 2))
    co.requestLeave(LeaveRequest(3, LeaveType.PERSONAL, 1))
    co.requestLeave(LeaveRequest(7, LeaveType.VACATION, 3))

    println("=== ${co.name} Roster ===")
    val sorted = co.employees.sortedBy { it.id }
    for (e in sorted) {
        val line = pad(e.name, 8) + pad(deptName(e.dept), 12) + pad(roleName(e.role), 10) + padNum(effectiveSalary(e), 7)
        println(line)
    }

    println("=== Department Headcount ===")
    for (dept in Department.values()) {
        val n = co.inDept(dept).size
        if (n > 0) {
            println("${deptName(dept)}: $n")
        }
    }

    println("=== Payroll Summary ===")
    println("Total payroll: ${co.totalPayroll()}")
    val effSalaries = co.employees.map { effectiveSalary(it) }
    println("Highest: ${effSalaries.maxOrNull() ?: 0}")
    println("Lowest: ${effSalaries.minOrNull() ?: 0}")
    val avg = co.totalPayroll() / co.employees.size
    println("Average: $avg")

    println("=== Engineering Team ===")
    val eng = co.inDept(Department.ENGINEERING).sortedByDescending { effectiveSalary(it) }
    for (e in eng) {
        println("${e.name} -> ${effectiveSalary(e)}")
    }

    println("=== Bonuses ===")
    val bonuses = ArrayList<Bonus>()
    bonuses.add(FlatBonus("Holiday", 500))
    bonuses.add(PercentBonus("Performance", 10))
    bonuses.add(PercentBonus("Retention", 5))
    for (b in bonuses) {
        println("${b.describe()}: ${b.amount(5000)}")
    }

    println("=== Pay Stubs ===")
    val totalBonus = bonuses.fold(0) { acc, b -> acc + b.amount(5000) }
    for (e in sorted) {
        val stub = co.payStubFor(e, totalBonus / co.employees.size)
        println("${pad(e.name, 8)} gross=${padNum(stub.gross, 6)} tax=${padNum(stub.tax, 5)} net=${padNum(stub.net, 6)}")
    }

    println("=== Leave Report ===")
    for (e in sorted) {
        val days = co.leaveDaysFor(e.id)
        if (days > 0) {
            println("${e.name}: $days day(s)")
        }
    }

    println("=== Lookup ===")
    val found = co.findById(5)
    if (found != null) {
        println("Found: ${found.name} (${roleName(found.role)})")
    }
    val missing = co.findById(99)
    println("Missing id 99 is null: ${missing == null}")

    println("=== Generic Roster ===")
    val names = Roster<String>()
    names.add("x")
    names.add("y")
    names.add("z")
    println("Roster size: ${names.size()}, first: ${names.get(0)}")

    println("=== Stats ===")
    val salaries = co.employees.map { effectiveSalary(it) }
    val above5k = salaries.filter { it > 5000 }
    println("Count above 5000: ${above5k.size}")
    println("Sum of all: ${salaries.sum()}")
    val seniorPlus = co.employees.filter { it.role == Role.SENIOR || it.role == Role.LEAD || it.role == Role.MANAGER }
    println("Senior+: ${seniorPlus.size}")
    val report = seniorPlus.sortedBy { it.name }.map { it.name }.joinToString(", ")
    println("Senior+ names: $report")

    println("=== Performance Reviews ===")
    val rb = ReviewBook()
    rb.record(Review(1, 1, 88))
    rb.record(Review(1, 2, 92))
    rb.record(Review(2, 1, 70))
    rb.record(Review(3, 1, 95))
    rb.record(Review(3, 2, 91))
    rb.record(Review(4, 1, 55))
    rb.record(Review(7, 1, 80))
    rb.record(Review(7, 2, 78))
    for (e in sorted) {
        val avg = rb.averageFor(e.id)
        if (avg > 0) {
            println("${pad(e.name, 8)} avg=${padNum(avg, 3)} ${ratingLabel(avg)}")
        }
    }

    println("=== Score Histogram ===")
    for (e in sorted) {
        val avg = rb.averageFor(e.id)
        if (avg > 0) {
            println("${pad(e.name, 8)}${bar(avg / 10)}")
        }
    }

    println("=== Top Performer ===")
    val picker = MaxPicker<Employee>({ rb.averageFor(it.id) })
    for (e in co.employees) {
        if (rb.averageFor(e.id) > 0) {
            picker.offer(e)
        }
    }
    val top = picker.pickTop()
    println("Top: ${top.name} (${rb.averageFor(top.id)})")

    println("=== Shift Coverage ===")
    val hours = listOf(2, 8, 9, 14, 15, 16, 20, 23)
    val shiftCounts = HashMap<String, Int>()
    for (h in hours) {
        val code = shiftCode(h)
        shiftCounts[code] = (shiftCounts[code] ?: 0) + 1
    }
    val shiftOrder = listOf("night", "morning", "afternoon", "evening")
    for (s in shiftOrder) {
        val c = shiftCounts[s] ?: 0
        println("$s: $c")
    }

    println("=== Quarters Worked ===")
    for (e in sorted) {
        val qs = rb.quartersFor(e.id)
        if (qs.isNotEmpty()) {
            println("${e.name}: ${qs.joinToString("-")}")
        }
    }

    println("=== Salary Bands ===")
    val bands = HashMap<String, Int>()
    for (e in co.employees) {
        val sal = effectiveSalary(e)
        val band = when {
            sal < 4000 -> "low"
            sal < 8000 -> "mid"
            else -> "high"
        }
        bands[band] = (bands[band] ?: 0) + 1
    }
    for (b in listOf("low", "mid", "high")) {
        println("$b: ${bands[b] ?: 0}")
    }

    println("=== Indexed Listing ===")
    for ((i, e) in sorted.withIndex()) {
        println("${i + 1}. ${e.name}")
    }

    println("=== Name Lengths ===")
    val byLen = co.employees.map { it.name.length }.sorted()
    println("Lengths: ${byLen.joinToString(",")}")
    println("Longest name: ${co.employees.map { it.name }.sortedByDescending { it.length }.first()}")

    println("=== Department Payroll ===")
    for (dept in Department.values()) {
        val team = co.inDept(dept)
        if (team.isNotEmpty()) {
            val pay = team.map { effectiveSalary(it) }.sum()
            println("${deptName(dept)}: $pay (${team.size})")
        }
    }

    println("=== Raise Simulation ===")
    var budget = 10000
    val ranked = co.employees.sortedByDescending { rb.averageFor(it.id) }
    for (e in ranked) {
        val avg = rb.averageFor(e.id)
        if (avg >= 85 && budget >= 500) {
            budget = budget - 500
            println("Raise for ${e.name} (avg $avg), budget left $budget")
        }
    }
    println("Final budget: $budget")

    println("=== Project Portfolio ===")
    val pf = Portfolio()
    pf.addProject(Project("ALPHA", "Platform", 3))
    pf.addProject(Project("BETA", "Mobile", 5))
    pf.addProject(Project("GAMMA", "Analytics", 1))
    pf.assign("ALPHA", 1)
    pf.assign("ALPHA", 3)
    pf.assign("ALPHA", 6)
    pf.assign("BETA", 2)
    pf.assign("BETA", 7)
    pf.assign("GAMMA", 5)
    for (p in pf.byPriority()) {
        println("[${p.priority}] ${p.code} ${p.name} team=${pf.teamSize(p.code)}")
    }
    println("Total assignments: ${pf.assignmentCount()}")
    println("=== Project Members ===")
    for (p in pf.byPriority()) {
        val ids = pf.assignments[p.code] ?: ArrayList<Int>()
        val names = ArrayList<String>()
        for (id in ids) {
            val emp = co.findById(id)
            if (emp != null) {
                names.add(emp.name)
            }
        }
        println("${p.code}: ${names.joinToString(", ")}")
    }
}
