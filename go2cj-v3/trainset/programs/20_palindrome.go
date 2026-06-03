package main

import "fmt"

func isPalindrome(s string) bool {
	n := len(s)
	for i := 0; i < n/2; i++ {
		if s[i] != s[n-1-i] {
			return false
		}
	}
	return true
}

func main() {
	fmt.Println(isPalindrome("level"))
	fmt.Println(isPalindrome("hello"))
	fmt.Println(isPalindrome("racecar"))
	fmt.Println(isPalindrome(""))
}
