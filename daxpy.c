#include <stdio.h>
#include <omp.h>

#define NUM_THREADS 4
void daxpy(int n, double a, double *x, double *y) {
    #pragma omp parallel for num_threads(NUM_THREADS)
    for (int i = 0; i < n; i++) {
        y[i] = a * x[i] + y[i];
    }
}

int main() {
    int n = 10;  // Smaller problem size
    double a = 2.0;
    double x[n], y[n];

    for (int i = 0; i < n; i++) {
        x[i] = i;
        y[i] = i * 2;
    }

    daxpy(n, a, x, y);

    printf("Done!\n");
    return 0;
}