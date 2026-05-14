package main

import "fmt"

func swap(a, b int) (int, int) {
	return b, a
}

func main() {
	x, y := 1, 2
	x, y = swap(x, y)
	fmt.Println(x)
	fmt.Println(y)
}
