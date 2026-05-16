package main

import "fmt"

func lcm(a int, b int) int {
	g := a
	t := b
	for t != 0 {
		r := g % t
		g = t
		t = r
	}
	return a * b / g
}

func main() {
	fmt.Println(lcm(4, 6))
	fmt.Println(lcm(7, 5))
	fmt.Println(lcm(12, 18))
}
