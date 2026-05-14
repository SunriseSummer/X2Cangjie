package main

import "fmt"

func max(a int, b int) int {
	if a > b {
		return a
	}
	return b
}

func min(a int, b int) int {
	if a < b {
		return a
	}
	return b
}

func main() {
	fmt.Println(max(3, 7))
	fmt.Println(min(3, 7))
}
