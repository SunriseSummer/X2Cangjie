package main

import "fmt"

func sumDigits(n int) int {
	s := 0
	for n > 0 {
		s = s + n%10
		n = n / 10
	}
	return s
}

func main() {
	fmt.Println(sumDigits(0))
	fmt.Println(sumDigits(123))
	fmt.Println(sumDigits(9876))
}
