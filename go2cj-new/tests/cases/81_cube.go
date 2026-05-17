package main

import "fmt"

func cube(x int) int {
	return x * x * x
}

func main() {
	for i := 0; i < 6; i++ {
		fmt.Println(cube(i))
	}
}
