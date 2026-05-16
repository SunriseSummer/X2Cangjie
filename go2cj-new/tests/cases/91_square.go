package main

import "fmt"

func square(x int) int {
	return x * x
}

func main() {
	for i := 0; i < 8; i++ {
		fmt.Println(square(i))
	}
}
