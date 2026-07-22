package main

import "fmt"

func sumToN(n int) int {
s := 0
for i := 1; i <= n; i++ {
s += i
}
return s
}

func main() {
fmt.Println(sumToN(10))
fmt.Println(sumToN(100))
fmt.Println(sumToN(1))
}
