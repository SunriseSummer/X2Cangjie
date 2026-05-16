package main

import "fmt"

func double(x int) int {
return x * 2
}

func inc(x int) int {
return x + 1
}

func main() {
fmt.Println(double(inc(5)))
}
