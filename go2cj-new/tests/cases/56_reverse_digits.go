package main

import "fmt"

func reverseDigits(n int) int {
	r := 0
	for n > 0 {
		r = r*10 + n%10
		n = n / 10
	}
	return r
}

func main() {
	fmt.Println(reverseDigits(123))
	fmt.Println(reverseDigits(1000))
	fmt.Println(reverseDigits(9876))
}
