package main

import "fmt"

func gcd(a int, b int) int {
	for b != 0 {
		a, b = b, a%b
	}
	return a
}

func main() {
	fmt.Println(gcd(48, 18))
	fmt.Println(gcd(100, 75))
	fmt.Println(gcd(7, 13))
}
