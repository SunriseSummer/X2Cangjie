main() {
    for (n in 1..=5) {
        let name = match (n) {
            case 1 => "one"
            case 2 | 3 => "few"
            case _ => "many"}
        println("${n} -> ${name}")
    }
}
