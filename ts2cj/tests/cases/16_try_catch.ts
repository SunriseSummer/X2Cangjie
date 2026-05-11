// 16 — try / catch / finally
function risky(x: number): number {
    if (x < 0) {
        throw new Error("negative");
    }
    return x * 2;
}

try {
    console.log(risky(5));
    console.log(risky(-1));
} catch (e) {
    console.log("caught error");
} finally {
    console.log("done");
}
