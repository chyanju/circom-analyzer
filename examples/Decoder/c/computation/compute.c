#include <stdio.h>
#include <klee/klee.h>
//typedef unsigned _BitInt(256) uint256;
//unsigned long long constant = 21888242871839275222246405745257275088548364400416034343698204186575808495617;
unsigned long long constant = 2188824287183927;


int main(int argc, char** argv) {

    /*
        template Decoder(w) {
            signal input inp;
            signal output out[w];
            signal output success;
            var lc=0;
            for (var i=0; i<w; i++) {
                out[i] <-- (inp == i) ? 1 : 0;
                out[i] * (inp-i) === 0;
                lc = lc + out[i];
            }
            lc ==> success;
            success * (success -1) === 0;
        }
        component main = Decoder(2);
    */

    // initialize circuit signals
    int in, w;
    int out[2], success;
    klee_make_symbolic(&in, sizeof(int), "in");
    klee_make_symbolic(&w, sizeof(int), "w");
    klee_assume(in >=0);
    // assume w = 2 to keep the program simple
    klee_assume(w == 2);

    klee_make_symbolic(&out, sizeof(int*), "out");
    klee_make_symbolic(&success, sizeof(int), "success");
    int lc = 0;

    // perform computation
    for (int i=0; i<w; i++) {
        if (in == i) klee_assume(out[i] == 1);
        else klee_assume(out[i] == 0);
        lc = lc + out[i];
    }
    klee_assume(success == lc);
    return 0;
}
