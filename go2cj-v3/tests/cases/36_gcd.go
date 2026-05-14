package main

import "fmt"

func gcd(a int, b int) int {
	if b == 0 {
		return a
	}
	return gcd(b, a%b)
}

func main() {
	fmt.Println(gcd(48, 18))
	fmt.Println(gcd(100, 75))
}
