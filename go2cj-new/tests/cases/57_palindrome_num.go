package main

import "fmt"

func isPalindromeNum(n int) bool {
	original := n
	r := 0
	for n > 0 {
		r = r*10 + n%10
		n = n / 10
	}
	return r == original
}

func main() {
	fmt.Println(isPalindromeNum(121))
	fmt.Println(isPalindromeNum(123))
	fmt.Println(isPalindromeNum(1221))
	fmt.Println(isPalindromeNum(7))
}
