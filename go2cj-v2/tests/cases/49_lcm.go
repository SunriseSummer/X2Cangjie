package main

import "fmt"

func lcm(a, b int) int {
	x, y := a, b
	for y != 0 {
		x, y = y, x%y
	}
	return a / x * b
}

func main() {
	fmt.Println(lcm(4, 6))
	fmt.Println(lcm(7, 5))
}
