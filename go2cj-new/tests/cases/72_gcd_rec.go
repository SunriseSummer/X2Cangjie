package main

import "fmt"

func gcdRec(a int, b int) int {
	if b == 0 {
		return a
	}
	return gcdRec(b, a%b)
}

func main() {
	fmt.Println(gcdRec(12, 18))
	fmt.Println(gcdRec(100, 25))
	fmt.Println(gcdRec(7, 11))
}
