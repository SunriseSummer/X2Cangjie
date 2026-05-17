package main

import "fmt"

func nthFibLoop(n int) int {
	if n < 2 {
		return n
	}
	a := 0
	b := 1
	for i := 2; i <= n; i++ {
		t := a + b
		a = b
		b = t
	}
	return b
}

func main() {
	fmt.Println(nthFibLoop(0))
	fmt.Println(nthFibLoop(1))
	fmt.Println(nthFibLoop(7))
	fmt.Println(nthFibLoop(15))
}
