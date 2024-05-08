#include <stdio.h>
#include <stdbool.h>
#include <klee/klee.h>
//typedef unsigned _BitInt(256) uint256;
//unsigned long long constant = 21888242871839275222246405745257275088548364400416034343698204186575808495617;
unsigned long long constant = 2188824287183927;


int main(int argc, char** argv) {

    // initialize circuit signals
    int in[2], out[2];
    klee_make_symbolic(&in, sizeof(int*), "in");
    klee_make_symbolic(&out, sizeof(int*), "out");

    for (int i=0; i<2; i++)
       klee_assume(in[i] >= 0);

    /*
        out[0] * (1-in[1]) === (1 + in[1]);
        out[1] * in[0] === out[0];
    */


    // check constraint satisfaction
    klee_assume((out[0] * (1 - in[1])) == (1 + in[1]));
    klee_assume((out[1] * in[0] == out[0]));
    return 0;
}
