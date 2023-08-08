package main

import "fmt"

func Hello(name string) string {
	message := fmt.Sprintf("Hey, %v. Welcome", name)
	return message
}

func main() {
	fmt.Println(Hello("something not me"))
}
