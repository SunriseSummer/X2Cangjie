package main

import "fmt"

func main() {
	count := 0
	for i := 1; i <= 20; i++ {
		if i%3 == 0 {
			count++
		}
	}
	fmt.Println(count)
}
