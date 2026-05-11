function divide(a: number, b: number): number {
    if (b === 0) {
        throw new Error("divide by zero");
    }
    return a / b;
}

function main(): void {
    try {
        console.log(divide(10, 2));
        console.log(divide(10, 0));
    } catch (e) {
        console.log("caught");
    } finally {
        console.log("done");
    }
}

main();
