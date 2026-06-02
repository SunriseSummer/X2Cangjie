import std.collection.*

func classifyAge(age: Int64): String {
    return if (age < 0) {
        "invalid"
    } else if (age < 13) {
        "child"
    } else if (age < 18) {
        "teen"
    } else if (age < 65) {
        "adult"
    } else {
        "senior"
    }
}

func fizzBuzz(n: Int64): String {
    return if ((n % 15) == 0) {
        "FizzBuzz"
    } else if ((n % 3) == 0) {
        "Fizz"
    } else if ((n % 5) == 0) {
        "Buzz"
    } else {
        n.toString()
    }
}

func describeNumber(n: Int64): String {
    return if (n < 0) {
        "negative"
    } else if (n == 0) {
        "zero"
    } else if (n >= 1 && n <= 10) {
        "small"
    } else if (n >= 11 && n <= 100) {
        "medium"
    } else {
        "large"
    }
}

func dayType(day: String): String {
    return match (day) {
        case "Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday" => "weekday"
        case "Saturday" | "Sunday" => "weekend"
        case _ => "unknown"}
}

main() {
    println(classifyAge(-1))
    println(classifyAge(5))
    println(classifyAge(15))
    println(classifyAge(30))
    println(classifyAge(70))
    let fb = ArrayList<String>()
    for (i in 1..=15) {
        fb.add(fizzBuzz(i))
    }
    println(String.join(collectArray<String>(fb.iterator().map({e => e.toString()})), delimiter: " "))
    println(describeNumber(-5))
    println(describeNumber(0))
    println(describeNumber(7))
    println(describeNumber(50))
    println(describeNumber(200))
    println(dayType("Monday"))
    println(dayType("Saturday"))
    println(dayType("Holiday"))
}
