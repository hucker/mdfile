public class Factorial {
    public static long factorial(int n) {
        return (n <= 1) ? 1 : n * factorial(n - 1); // Base case + Recursive case
    }

    public static void main(String[] args) {
        System.out.println(factorial(5)); // Example: prints 120
    }
}
