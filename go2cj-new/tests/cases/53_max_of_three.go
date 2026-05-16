package main

import "fmt"

func maxOfThree(a int, b int, c int) int {
	m := a
	if b > m {
		m = b
	}
	if c > m {
		m = c
	}
	return m
}

func main() {
	fmt.Println(maxOfThree(1, 2, 3))
	fmt.Println(maxOfThree(9, 4, 5))
	fmt.Println(maxOfThree(-1, -2, -3))
}
