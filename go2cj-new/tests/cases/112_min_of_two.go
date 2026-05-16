package main

import "fmt"

func minOfTwo(a int, b int) int {
	if a < b {
		return a
	}
	return b
}

func main() {
	fmt.Println(minOfTwo(3, 5))
	fmt.Println(minOfTwo(10, 2))
	fmt.Println(minOfTwo(-1, -7))
}
