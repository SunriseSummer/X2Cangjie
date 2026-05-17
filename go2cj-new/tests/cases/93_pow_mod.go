package main

import "fmt"

func powMod(base int, exp int, m int) int {
	r := 1
	b := base % m
	e := exp
	for e > 0 {
		if e%2 == 1 {
			r = r * b % m
		}
		b = b * b % m
		e = e / 2
	}
	return r
}

func main() {
	fmt.Println(powMod(2, 10, 1000))
	fmt.Println(powMod(3, 7, 13))
	fmt.Println(powMod(5, 0, 7))
}
