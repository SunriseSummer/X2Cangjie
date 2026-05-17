package main

import "fmt"

func sign(x int) int {
	if x > 0 {
		return 1
	}
	if x < 0 {
		return -1
	}
	return 0
}

func main() {
	fmt.Println(sign(5))
	fmt.Println(sign(-3))
	fmt.Println(sign(0))
}
