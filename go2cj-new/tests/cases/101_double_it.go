package main

import "fmt"

func doubleIt(x int) int {
	return x + x
}

func main() {
	for i := 0; i < 5; i++ {
		fmt.Println(doubleIt(i))
	}
}
