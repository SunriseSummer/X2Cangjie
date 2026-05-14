package main

import "fmt"

func dayName(d int) string {
switch d {
case 1:
return "Mon"
case 2:
return "Tue"
case 3:
return "Wed"
default:
return "?"
}
}

func main() {
fmt.Println(dayName(1))
fmt.Println(dayName(2))
fmt.Println(dayName(3))
fmt.Println(dayName(7))
}
