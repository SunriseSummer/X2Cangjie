main() {
    for (i in 1..=15) {
        let line = if ((i % 15) == 0) {
            "FizzBuzz"
        } else if ((i % 3) == 0) {
            "Fizz"
        } else if ((i % 5) == 0) {
            "Buzz"
        } else {
            "${i}"
        }
        println(line)
    }
}
