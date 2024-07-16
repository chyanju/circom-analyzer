pragma circom 2.0.0;

template IsZero() {
    signal input in;
    signal output out;
    out <-- in==0 ? 1 : 0;
    in*out === 0;
}

component main = IsZero();