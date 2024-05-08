#include <stdio.h>
#include <klee/klee.h>
//typedef unsigned _BitInt(256) uint256;
//unsigned long long constant = 21888242871839275222246405745257275088548364400416034343698204186575808495617;
unsigned long long constant = 2188824287183927;


int main(int argc, char** argv) {

    // initialize circuit signals
    int in, out;
    klee_make_symbolic(&in, sizeof(int), "in");
    klee_make_symbolic(&out, sizeof(int), "out");
    klee_assume(in >= 0);

    // check constraint satisfaction
    klee_assume((in * out) == 0);
    return 0;
}
