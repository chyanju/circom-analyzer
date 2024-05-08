#include <stdio.h>
#include <klee/klee.h>
//typedef unsigned _BitInt(256) uint256;
//unsigned long long constant = 21888242871839275222246405745257275088548364400416034343698204186575808495617;
unsigned long long constant = 2188824287183927;


int main(int argc, char** argv) {

    /*
    signal input in[2];
    signal output out[2];

    out[0] <-- (1 + in[1]) / (1 - in[1]);
    out[1] <-- out[0] / in[0];

    */

    // initialize circuit signals
    int in[2], out[2];
    klee_make_symbolic(&in, sizeof(int*), "in");
    klee_make_symbolic(&out, sizeof(int*), "out");
    klee_assume(in[0] >= 0);
    klee_assume(in[1] >= 0);

    // perform computation
    klee_assume((1 - in[1]) != 0);
    klee_assume(out[0] == (1 + in[1])/(1 - in[1]));
    klee_assume(in[0] != 0);
    klee_assume(out[1] == out[0] / in[0]);

    return 0;
}
