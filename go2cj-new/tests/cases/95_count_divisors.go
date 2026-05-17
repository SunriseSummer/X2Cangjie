package main

import "fmt"

func countDivisors(n int) int {
	c := 0
	for i := 1; i <= n; i++ {
		if n%i == 0 {
			c = c + 1
		}
	}
	return c
}

func main() {
	fmt.Println(countDivisors(1))
	fmt.Println(countDivisors(6))
	fmt.Println(countDivisors(12))
	fmt.Println(countDivisors(36))
}
