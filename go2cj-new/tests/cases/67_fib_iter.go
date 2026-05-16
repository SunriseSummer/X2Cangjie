package main

import "fmt"

func fibIter(n int) int {
	a := 0
	b := 1
	for i := 0; i < n; i++ {
		t := a + b
		a = b
		b = t
	}
	return a
}

func main() {
	for i := 0; i < 10; i++ {
		fmt.Println(fibIter(i))
	}
}
