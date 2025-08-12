#include <stdio.h>

// Recursive factorial function
unsigned long long factorial(int n) {
    if (n < 0) {
        printf("Factorial is not defined for negative numbers.\n");
        return 0;
    }
    if (n == 0 || n == 1) {
        return 1; // Base case
    }
    return n * factorial(n - 1); // Recursive case
}
