package proj_stringops

main() {
    let utils = StringUtils()
    println("Reverse 'hello': ${utils.reverseString("hello")}")
    println("Reverse 'abcde': ${utils.reverseString("abcde")}")
    println("Vowels in 'Hello World': ${utils.countVowels("Hello World")}")
    println("Vowels in 'xyz': ${utils.countVowels("xyz")}")
    println("Is 'racecar' palindrome: ${utils.isPalindrome("racecar")}")
    println("Is 'hello' palindrome: ${utils.isPalindrome("hello")}")
    println("Is 'abba' palindrome: ${utils.isPalindrome("abba")}")
    println("Words in 'hello world foo': ${utils.wordCount("hello world foo")}")
    println("Words in '': ${utils.wordCount("")}")
    println("Capitalize 'hello': ${utils.capitalize("hello")}")
    let emptyResult = utils.capitalize("")
    println("Capitalize empty: [${emptyResult}]")
}
