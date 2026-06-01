import std.collection.*
import std.deriving.*
import std.sort.*

@Derive[Equatable]
enum Department <: ToString {
    | ENGINEERING | SALES | SUPPORT | FINANCE | HR
    public func toString(): String {
    return match (this) {
                case ENGINEERING => "ENGINEERING"
            case SALES => "SALES"
            case SUPPORT => "SUPPORT"
            case FINANCE => "FINANCE"
            case HR => "HR"
}
    }
}

@Derive[Equatable]
enum Role <: ToString {
    | JUNIOR | MID | SENIOR | LEAD | MANAGER
    public func toString(): String {
    return match (this) {
                case JUNIOR => "JUNIOR"
            case MID => "MID"
            case SENIOR => "SENIOR"
            case LEAD => "LEAD"
            case MANAGER => "MANAGER"
}
    }
}

@Derive[Equatable]
enum LeaveType <: ToString {
    | VACATION | SICK | PERSONAL
    public func toString(): String {
    return match (this) {
                case VACATION => "VACATION"
            case SICK => "SICK"
            case PERSONAL => "PERSONAL"
}
    }
}

class Employee <: ToString {
    let id: Int64
    let name: String
    let dept: Department
    let role: Role
    let baseSalary: Int64
    init(id: Int64, name: String, dept: Department, role: Role, baseSalary: Int64) {
        this.id = id
        this.name = name
        this.dept = dept
        this.role = role
        this.baseSalary = baseSalary
    }
    public func toString(): String {
        return "Employee(id=${this.id}, name=${this.name}, dept=${this.dept}, role=${this.role}, baseSalary=${this.baseSalary})"
    }
}

class LeaveRequest <: ToString {
    let empId: Int64
    let `type`: LeaveType
    let days: Int64
    init(empId: Int64, `type`: LeaveType, days: Int64) {
        this.empId = empId
        this.`type` = `type`
        this.days = days
    }
    public func toString(): String {
        return "LeaveRequest(empId=${this.empId}, `type`=${this.`type`}, days=${this.days})"
    }
}

class PayStub <: ToString {
    let empId: Int64
    let gross: Int64
    let tax: Int64
    let net: Int64
    init(empId: Int64, gross: Int64, tax: Int64, net: Int64) {
        this.empId = empId
        this.gross = gross
        this.tax = tax
        this.net = net
    }
    public func toString(): String {
        return "PayStub(empId=${this.empId}, gross=${this.gross}, tax=${this.tax}, net=${this.net})"
    }
}

interface Describable {
    func describe(): String
}

abstract class Bonus <: Describable {
    let label: String
    init(label: String) {
        this.label = label
    }
    public func amount(base: Int64): Int64
    public func describe(): String {
        return "${label} bonus"
    }
}

class FlatBonus <: Bonus {
    let value: Int64
    init(label: String, value: Int64) {
        super(label)
        this.value = value
    }
    public func amount(base: Int64): Int64 {
        return value
    }
}

class PercentBonus <: Bonus {
    let percent: Int64
    init(label: String, percent: Int64) {
        super(label)
        this.percent = percent
    }
    public func amount(base: Int64): Int64 {
        return (base * percent) / 100
    }
}

class Roster<T> {
    let items = ArrayList<T>()
    func add(x: T) {
        items.add(x)
    }
    func size(): Int64 {
        return items.size
    }
    func get(i: Int64): T {
        return items[i]
    }
}

func roleMultiplier(role: Role): Int64 {
    return match (role) {
        case Role.JUNIOR => 100
        case Role.MID => 120
        case Role.SENIOR => 150
        case Role.LEAD => 180
        case Role.MANAGER => 220}
}

func roleName(role: Role): String {
    return match (role) {
        case Role.JUNIOR => "Junior"
        case Role.MID => "Mid"
        case Role.SENIOR => "Senior"
        case Role.LEAD => "Lead"
        case Role.MANAGER => "Manager"}
}

func deptName(dept: Department): String {
    return match (dept) {
        case Department.ENGINEERING => "Engineering"
        case Department.SALES => "Sales"
        case Department.SUPPORT => "Support"
        case Department.FINANCE => "Finance"
        case Department.HR => "HR"}
}

func taxFor(gross: Int64): Int64 {
    return if (gross >= 0 && gross <= 2999) {
        (gross * 5) / 100
    } else if (gross >= 3000 && gross <= 5999) {
        (gross * 10) / 100
    } else if (gross >= 6000 && gross <= 9999) {
        (gross * 18) / 100
    } else {
        (gross * 25) / 100
    }
}

func effectiveSalary(emp: Employee): Int64 {
    return (emp.baseSalary * roleMultiplier(emp.role)) / 100
}

class Company {
    let name: String
    init(name: String) {
        this.name = name
    }
    let employees = ArrayList<Employee>()
    let leaves = ArrayList<LeaveRequest>()
    func hire(e: Employee) {
        employees.add(e)
    }
    func requestLeave(r: LeaveRequest) {
        leaves.add(r)
    }
    func findById(id: Int64): ?Employee {
        for (e in employees) {
            if (e.id == id) {
                return e
            }
        }
        return None
    }
    func inDept(dept: Department): ArrayList<Employee> {
        let out = ArrayList<Employee>()
        for (e in employees) {
            if (e.dept == dept) {
                out.add(e)
            }
        }
        return out
    }
    func totalPayroll(): Int64 {
        var total = 0
        for (e in employees) {
            total = total + effectiveSalary(e)
        }
        return total
    }
    func leaveDaysFor(empId: Int64): Int64 {
        var sum = 0
        for (r in leaves) {
            if (r.empId == empId) {
                sum = sum + r.days
            }
        }
        return sum
    }
    func payStubFor(emp: Employee, bonus: Int64): PayStub {
        let gross = effectiveSalary(emp) + bonus
        let tax = taxFor(gross)
        return PayStub(emp.id, gross, tax, gross - tax)
    }
}

func pad(s: String, width: Int64): String {
    var out = s
    while (out.size < width) {
        out = out + " "
    }
    return out
}

func padNum(n: Int64, width: Int64): String {
    var s = n.toString()
    while (s.size < width) {
        s = " " + s
    }
    return s
}

class MaxPicker<T> {
    let keyOf: (T) -> Int64
    init(keyOf: (T) -> Int64) {
        this.keyOf = keyOf
    }
    let items = ArrayList<T>()
    func offer(x: T) {
        items.add(x)
    }
    func pickTop(): T {
        var bestIdx = 0
        var bestKey = keyOf(items[0])
        for (i in 1..items.size) {
            let k = keyOf(items[i])
            if (k > bestKey) {
                bestKey = k
                bestIdx = i
            }
        }
        return items[bestIdx]
    }
}

class Review <: ToString {
    let empId: Int64
    let quarter: Int64
    let score: Int64
    init(empId: Int64, quarter: Int64, score: Int64) {
        this.empId = empId
        this.quarter = quarter
        this.score = score
    }
    public func toString(): String {
        return "Review(empId=${this.empId}, quarter=${this.quarter}, score=${this.score})"
    }
}

func ratingLabel(avg: Int64): String {
    return if (avg >= 90 && avg <= 100) {
        "Outstanding"
    } else if (avg >= 75 && avg <= 89) {
        "Exceeds"
    } else if (avg >= 60 && avg <= 74) {
        "Meets"
    } else if (avg >= 40 && avg <= 59) {
        "Developing"
    } else {
        "Needs Improvement"
    }
}

class ReviewBook {
    let reviews = ArrayList<Review>()
    func record(r: Review) {
        reviews.add(r)
    }
    func averageFor(empId: Int64): Int64 {
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
    func quartersFor(empId: Int64): ArrayList<Int64> {
        let out = ArrayList<Int64>()
        for (r in reviews) {
            if (r.empId == empId) {
                out.add(r.quarter)
            }
        }
        return out
    }
}

func bar(n: Int64): String {
    return ("#" * n)
}

func shiftCode(hour: Int64): String {
    return if (hour < 6) {
        "night"
    } else if (hour < 12) {
        "morning"
    } else if (hour < 18) {
        "afternoon"
    } else {
        "evening"
    }
}

class Project <: ToString {
    let code: String
    let name: String
    let priority: Int64
    init(code: String, name: String, priority: Int64) {
        this.code = code
        this.name = name
        this.priority = priority
    }
    public func toString(): String {
        return "Project(code=${this.code}, name=${this.name}, priority=${this.priority})"
    }
}

class Portfolio {
    let projects = ArrayList<Project>()
    let assignments = HashMap<String, ArrayList<Int64>>()
    func addProject(p: Project) {
        projects.add(p)
        assignments[p.code] = ArrayList<Int64>()
    }
    func assign(code: String, empId: Int64) {
        assignments.get(code)?.add(empId)
    }
    func teamSize(code: String): Int64 {
        return assignments.get(code)?.size ?? 0
    }
    func byPriority(): ArrayList<Project> {
        return ({ => let _s = collectArrayList(projects.iterator()); sort(_s, key: { it => it.priority }, stable: true, descending: true); _s })()
    }
    func assignmentCount(): Int64 {
        var total = 0
        for (p in projects) {
            total = total + teamSize(p.code)
        }
        return total
    }
}

main() {
    let co = Company("Acme")
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
    let sorted = ({ => let _s = collectArrayList(co.employees.iterator()); sort(_s, key: { it => it.id }, stable: true); _s })()
    for (e in sorted) {
        let line = ((pad(e.name, 8) + pad(deptName(e.dept), 12)) + pad(roleName(e.role), 10)) + padNum(effectiveSalary(e), 7)
        println(line)
    }
    println("=== Department Headcount ===")
    for (dept in [Department.ENGINEERING, Department.SALES, Department.SUPPORT, Department.FINANCE, Department.HR]) {
        let n = co.inDept(dept).size
        if (n > 0) {
            println("${deptName(dept)}: ${n}")
        }
    }
    println("=== Payroll Summary ===")
    println("Total payroll: ${co.totalPayroll()}")
    let effSalaries = collectArrayList(co.employees.iterator().map({ it => effectiveSalary(it) }))
    println("Highest: ${effSalaries.iterator().reduce({a, b => if (a > b) { a } else { b }}) ?? 0}")
    println("Lowest: ${effSalaries.iterator().reduce({a, b => if (a < b) { a } else { b }}) ?? 0}")
    let avg = co.totalPayroll() / co.employees.size
    println("Average: ${avg}")
    println("=== Engineering Team ===")
    let eng = ({ => let _s = collectArrayList(co.inDept(Department.ENGINEERING).iterator()); sort(_s, key: { it => effectiveSalary(it) }, stable: true, descending: true); _s })()
    for (e in eng) {
        println("${e.name} -> ${effectiveSalary(e)}")
    }
    println("=== Bonuses ===")
    let bonuses = ArrayList<Bonus>()
    bonuses.add(FlatBonus("Holiday", 500))
    bonuses.add(PercentBonus("Performance", 10))
    bonuses.add(PercentBonus("Retention", 5))
    for (b in bonuses) {
        println("${b.describe()}: ${b.amount(5000)}")
    }
    println("=== Pay Stubs ===")
    let totalBonus = bonuses.iterator().fold<Int64>(0, { acc, b => acc + b.amount(5000) })
    for (e in sorted) {
        let stub = co.payStubFor(e, totalBonus / co.employees.size)
        println("${pad(e.name, 8)} gross=${padNum(stub.gross, 6)} tax=${padNum(stub.tax, 5)} net=${padNum(stub.net, 6)}")
    }
    println("=== Leave Report ===")
    for (e in sorted) {
        let days = co.leaveDaysFor(e.id)
        if (days > 0) {
            println("${e.name}: ${days} day(s)")
        }
    }
    println("=== Lookup ===")
    let found = co.findById(5)
    if (let Some(found) <- found) {
        println("Found: ${found.name} (${roleName(found.role)})")
    }
    let missing = co.findById(99)
    println("Missing id 99 is null: ${missing.isNone()}")
    println("=== Generic Roster ===")
    let names = Roster<String>()
    names.add("x")
    names.add("y")
    names.add("z")
    println("Roster size: ${names.size()}, first: ${names.get(0)}")
    println("=== Stats ===")
    let salaries = collectArrayList(co.employees.iterator().map({ it => effectiveSalary(it) }))
    let above5k = collectArrayList(salaries.iterator().filter({ it => it > 5000 }))
    println("Count above 5000: ${above5k.size}")
    println("Sum of all: ${salaries.iterator().fold<Int64>(0, {acc, x => acc + x})}")
    let seniorPlus = collectArrayList(co.employees.iterator().filter({ it => ((it.role == Role.SENIOR) || (it.role == Role.LEAD)) || (it.role == Role.MANAGER) }))
    println("Senior+: ${seniorPlus.size}")
    let report = String.join(collectArray<String>(collectArrayList(({ => let _s = collectArrayList(seniorPlus.iterator()); sort(_s, key: { it => it.name }, stable: true); _s })().iterator().map({ it => it.name })).iterator().map({e => e.toString()})), delimiter: ", ")
    println("Senior+ names: ${report}")
    println("=== Performance Reviews ===")
    let rb = ReviewBook()
    rb.record(Review(1, 1, 88))
    rb.record(Review(1, 2, 92))
    rb.record(Review(2, 1, 70))
    rb.record(Review(3, 1, 95))
    rb.record(Review(3, 2, 91))
    rb.record(Review(4, 1, 55))
    rb.record(Review(7, 1, 80))
    rb.record(Review(7, 2, 78))
    for (e in sorted) {
        let avg = rb.averageFor(e.id)
        if (avg > 0) {
            println("${pad(e.name, 8)} avg=${padNum(avg, 3)} ${ratingLabel(avg)}")
        }
    }
    println("=== Score Histogram ===")
    for (e in sorted) {
        let avg = rb.averageFor(e.id)
        if (avg > 0) {
            println("${pad(e.name, 8)}${bar(avg / 10)}")
        }
    }
    println("=== Top Performer ===")
    let picker = MaxPicker<Employee>({ it => rb.averageFor(it.id) })
    for (e in co.employees) {
        if (rb.averageFor(e.id) > 0) {
            picker.offer(e)
        }
    }
    let top = picker.pickTop()
    println("Top: ${top.name} (${rb.averageFor(top.id)})")
    println("=== Shift Coverage ===")
    let hours = ArrayList([2, 8, 9, 14, 15, 16, 20, 23])
    let shiftCounts = HashMap<String, Int64>()
    for (h in hours) {
        let code = shiftCode(h)
        shiftCounts[code] = (shiftCounts.get(code) ?? 0) + 1
    }
    let shiftOrder = ArrayList(["night", "morning", "afternoon", "evening"])
    for (s in shiftOrder) {
        let c = shiftCounts.get(s) ?? 0
        println("${s}: ${c}")
    }
    println("=== Quarters Worked ===")
    for (e in sorted) {
        let qs = rb.quartersFor(e.id)
        if (!(qs.isEmpty())) {
            println("${e.name}: ${String.join(collectArray<String>(qs.iterator().map({e => e.toString()})), delimiter: "-")}")
        }
    }
    println("=== Salary Bands ===")
    let bands = HashMap<String, Int64>()
    for (e in co.employees) {
        let sal = effectiveSalary(e)
        let band = if (sal < 4000) {
            "low"
        } else if (sal < 8000) {
            "mid"
        } else {
            "high"
        }
        bands[band] = (bands.get(band) ?? 0) + 1
    }
    for (b in ArrayList(["low", "mid", "high"])) {
        println("${b}: ${bands.get(b) ?? 0}")
    }
    println("=== Indexed Listing ===")
    for ((i, e) in sorted.iterator().enumerate()) {
        println("${i + 1}. ${e.name}")
    }
    println("=== Name Lengths ===")
    let byLen = ({ => let _s = collectArrayList(collectArrayList(co.employees.iterator().map({ it => it.name.size })).iterator()); sort(_s, stable: true); _s })()
    println("Lengths: ${String.join(collectArray<String>(byLen.iterator().map({e => e.toString()})), delimiter: ",")}")
    println("Longest name: ${({ => let _s = collectArrayList(collectArrayList(co.employees.iterator().map({ it => it.name })).iterator()); sort(_s, key: { it => it.size }, stable: true, descending: true); _s })()[0]}")
    println("=== Department Payroll ===")
    for (dept in [Department.ENGINEERING, Department.SALES, Department.SUPPORT, Department.FINANCE, Department.HR]) {
        let team = co.inDept(dept)
        if (!(team.isEmpty())) {
            let pay = collectArrayList(team.iterator().map({ it => effectiveSalary(it) })).iterator().fold<Int64>(0, {acc, x => acc + x})
            println("${deptName(dept)}: ${pay} (${team.size})")
        }
    }
    println("=== Raise Simulation ===")
    var budget = 10000
    let ranked = ({ => let _s = collectArrayList(co.employees.iterator()); sort(_s, key: { it => rb.averageFor(it.id) }, stable: true, descending: true); _s })()
    for (e in ranked) {
        let avg = rb.averageFor(e.id)
        if ((avg >= 85) && (budget >= 500)) {
            budget = budget - 500
            println("Raise for ${e.name} (avg ${avg}), budget left ${budget}")
        }
    }
    println("Final budget: ${budget}")
    println("=== Project Portfolio ===")
    let pf = Portfolio()
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
        let ids = pf.assignments.get(p.code) ?? ArrayList<Int64>()
        let names = ArrayList<String>()
        for (id in ids) {
            let emp = co.findById(id)
            if (let Some(emp) <- emp) {
                names.add(emp.name)
            }
        }
        println("${p.code}: ${String.join(collectArray<String>(names.iterator().map({e => e.toString()})), delimiter: ", ")}")
    }
}
