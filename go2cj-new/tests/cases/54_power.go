package main

import "fmt"

func power(base int, exp int) int {
	r := 1
	for i := 0; i < exp; i++ {
		r = r * base
	}
	return r
}

func main() {
	fmt.Println(power(2, 0))
	fmt.Println(power(2, 10))
	fmt.Println(power(3, 4))
}
