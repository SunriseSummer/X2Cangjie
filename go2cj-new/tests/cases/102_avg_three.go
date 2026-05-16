package main

import "fmt"

func avgInt(a int, b int, c int) int {
	return (a + b + c) / 3
}

func main() {
	fmt.Println(avgInt(1, 2, 3))
	fmt.Println(avgInt(10, 20, 30))
	fmt.Println(avgInt(7, 7, 7))
}
