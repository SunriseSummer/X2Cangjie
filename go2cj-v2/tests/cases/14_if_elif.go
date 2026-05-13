package main

import "fmt"

func grade(s int) string {
if s >= 90 {
return "A"
} else if s >= 80 {
return "B"
} else if s >= 70 {
return "C"
} else {
return "F"
}
}

func main() {
fmt.Println(grade(95))
fmt.Println(grade(85))
fmt.Println(grade(75))
fmt.Println(grade(50))
}
