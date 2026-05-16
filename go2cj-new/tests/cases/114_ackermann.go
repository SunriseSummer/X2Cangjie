package main

import "fmt"

func ackermannSmall(m int, n int) int {
	if m == 0 {
		return n + 1
	}
	if n == 0 {
		return ackermannSmall(m-1, 1)
	}
	return ackermannSmall(m-1, ackermannSmall(m, n-1))
}

func main() {
	fmt.Println(ackermannSmall(0, 0))
	fmt.Println(ackermannSmall(1, 1))
	fmt.Println(ackermannSmall(2, 3))
	fmt.Println(ackermannSmall(3, 3))
}
