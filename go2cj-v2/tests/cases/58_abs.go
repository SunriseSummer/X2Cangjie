package main

import "fmt"

func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

func main() {
	fmt.Println(abs(-7))
	fmt.Println(abs(0))
	fmt.Println(abs(42))
}
