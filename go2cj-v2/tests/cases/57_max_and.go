package main

import "fmt"

func main() {
	a := 5
	b := 3
	if a > b {
		fmt.Println(a)
	} else {
		fmt.Println(b)
	}
	if a > b && a > 0 {
		fmt.Println("both")
	}
}
