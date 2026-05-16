package main

import "fmt"

func countDigits(n int) int {
	if n == 0 {
		return 1
	}
	c := 0
	for n > 0 {
		c = c + 1
		n = n / 10
	}
	return c
}

func main() {
	fmt.Println(countDigits(0))
	fmt.Println(countDigits(9))
	fmt.Println(countDigits(123))
	fmt.Println(countDigits(1000000))
}
