document.addEventListener("DOMContentLoaded", function () {
    const num1 = document.getElementById("num1");
    const num2 = document.getElementById("num2");
    const operation = document.getElementById("operation");
    const calculateBtn = document.getElementById("calculate");
    const resultDiv = document.getElementById("result");

    calculateBtn.addEventListener("click", function () {
        const a = parseFloat(num1.value);
        const b = parseFloat(num2.value);
        const op = operation.value;

        if (isNaN(a) || isNaN(b)) {
            resultDiv.textContent = "Palun sisesta kehtivad arvud!";
            resultDiv.className = "error";
            return;
        }

        let result;
        switch (op) {
            case "add":
                result = a + b;
                break;
            case "sub":
                result = a - b;
                break;
            case "mul":
                result = a * b;
                break;
            case "div":
                if (b === 0) {
                    resultDiv.textContent = "Nulliga jagamine pole lubatud!";
                    resultDiv.className = "error";
                    return;
                }
                result = a / b;
                break;
            default:
                result = "Tundmatu tehe";
        }

        resultDiv.textContent = "Vastus: " + result;
        resultDiv.className = "";
    });
});
