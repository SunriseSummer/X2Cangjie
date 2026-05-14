package main

import "fmt"

func swap(a int, b int) (int, int) {
	return b, a
}

func main() {
	a, b := swap(1, 2)
	fmt.Println(a)
	fmt.Println(b)
}
