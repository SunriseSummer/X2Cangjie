package main

import "fmt"

func gcd(a, b int) int {
	for b != 0 {
		a, b = b, a%b
	}
	return a
}

func lcm(a, b int) int {
	return a / gcd(a, b) * b
}

func main() {
	fmt.Println(lcm(4, 6))
	fmt.Println(lcm(12, 18))
	fmt.Println(lcm(7, 5))
	fmt.Println(lcm(100, 80))
}
