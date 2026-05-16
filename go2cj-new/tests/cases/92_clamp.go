package main

import "fmt"

func clamp(x int, lo int, hi int) int {
	if x < lo {
		return lo
	}
	if x > hi {
		return hi
	}
	return x
}

func main() {
	fmt.Println(clamp(5, 0, 10))
	fmt.Println(clamp(-3, 0, 10))
	fmt.Println(clamp(15, 0, 10))
}
