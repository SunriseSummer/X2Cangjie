package main

import "fmt"

func triangleNumber(n int) int {
	return n * (n + 1) / 2
}

func main() {
	fmt.Println(triangleNumber(0))
	fmt.Println(triangleNumber(1))
	fmt.Println(triangleNumber(5))
	fmt.Println(triangleNumber(10))
}
