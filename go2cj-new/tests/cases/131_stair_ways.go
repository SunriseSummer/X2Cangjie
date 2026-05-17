package main

import "fmt"

func ways(n int) int {
if n <= 2 {
return n
}
a, b := 1, 2
for i := 3; i <= n; i++ {
a, b = b, a+b
}
return b
}

func main() {
fmt.Println(ways(3))
fmt.Println(ways(5))
fmt.Println(ways(8))
}
