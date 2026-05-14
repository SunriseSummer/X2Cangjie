package main

import "fmt"

func swap(a int, b int) (int, int) {
return b, a
}

func main() {
x, y := swap(1, 2)
fmt.Println(x)
fmt.Println(y)
}
