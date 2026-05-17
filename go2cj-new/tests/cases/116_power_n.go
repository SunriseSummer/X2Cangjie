package main

import "fmt"

func powerN(base int, n int) int {
	r := 1
	for i := 0; i < n; i++ {
		r = r * base
	}
	return r
}

func main() {
	fmt.Println(powerN(2, 10))
	fmt.Println(powerN(3, 5))
	fmt.Println(powerN(7, 0))
	fmt.Println(powerN(5, 4))
}
