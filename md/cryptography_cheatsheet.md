# Cryptography cheatsheet

A few days ago, I was having a chat with an AI researcher who is trying to figure out which cryptographic primitives are most suitable for fulfilling his privacy requirements for AI. He mentioned how lost and confused he felt regarding the numerous resources he found online. I argued that understanding the interfaces of these privacy technologies alone already gives you a way to pick the right components for the solution he has in mind. The deep dive into the underlying math can wait.

So here's the cheatsheet describing the APIs for [programmable cryptography](https://0xparc.org/writings/programmable-cryptography-1)-related primitives and a list of libraries to build with them. I assume the reader is already familiar with basic concepts such as asymmetric-key encryption, hash functions, and digital signatures.

## 1. ZK-SNARK 

A SNARK is a cryptographic primitive that allows a prover to prove that he/she executed a program, say expressed via `f` with inputs `x_1, x_2`, all while keeping the time required to verify it incredibly shorter than the time it would take to redo the entire computation.

The *optional* ZK part allows to hide some input, for example `x_2`. The example later will make such differences more evident. Hereafter, we'll use the term ZK-SNARK also for those applications in which the ZK component is not used.

#### Core APIs

- `setup(f)` -> `(pk, vk)`: Generate proving and verification keys tied to a specific program `f`
- `prove(pk, public_inputs, private_inputs)` -> `proof`: Create the proof.
- `verify(vk, public_inputs, proof)` -> `bool`: Check if the proof is valid.

In this example, Alice - the prover - wants to prove to a verifier - Bob the bouncer - that she is over 18 years old to enter the club, all without revealing her actual age.

#### Example: ZK-SNARK - private age verification (without provenance check)

```typescript
// The program logic
function AgeGate(actualAge) {
  assert(actualAge >= 18)); 
}

// Note: at setup time, the inputs are not known
// The same pk, vk can be used with any combination of inputs
ZK.setup(AgeGate) -> pk, vk

// Prover - Alice looking to enter a club
const proof = ZK.prove(pk, null, { actualAge: 21 });

// Verifier - Bob the bouncer
const isValid = ZK.verify(vk, null, proof); 

// Result: true (but verifier never saw the actualAge)
```

Unfortunately, the previous example is not secure since Alice can input any `actualAge` they want. A more robust logic would be to check whether the `actualAge` has been attested, for example, via a government-issued signature form, identified by its globally known public key `govPubKey`.

#### Example: ZK-SNARK - private age verification (with provenance check)

```typescript
// The program logic
function AgeGateWithProvenanceCheck(actualAge, signature, govPubKey) {
    assert(actualAge >= 18));
    assert(VerifySignature(signature, actualAge, govPubKey)); 
} 

ZK.setup(AgeGateWithProvenanceCheck) -> pk, vk 

// Prover
const proof = ZK.prove(pk, { govPubKey: 0x123  },  { actualAge: 21, signature: aaa });

// Verifier
const isValid = ZK.verify(vk, { govPubKey: 0x123  }, proof); 

// Result: true (but verifier never saw the actualAge or the signature)
```

The next example only leverages the efficiency property (and not the privacy), therefore this is *technically* not ZK. The verifier is able to assess that `expected_result` is the result of recursive hashing of `seed` a thousand times without actually having to redo these labourious computation themselves. In other words, they can verify that a computation was executed as expected more efficiently.

#### Example: ZK-SNARK - recursive hash check

```typescript
// The program logic
function RecursiveHashChain(seed, expected_result) {
    current_hash = seed
        
    for _ in range(1000):
        current_hash = hash(current_hash)
            
    # The constraint: the result after 1000 iteration must match the expected_result
    assert(current_hash = expected_result)

} 

ZK.setup(RecursiveHashChain) -> pk, vk

// Prover 
const proof = ZK.prove(pk, { seed: aaa, expected_result: bbb }, null);

// Verifier
const isValid = ZK.verify(vk, { seed: aaa, expected_result: bbb }, proof);

// Result: true (both the seed and the expected_result are known to the verifier)
```

### Tooling

Circom/snarkJS, Noir, Gnark, SP1

## 2. FHE

Fully Homomorphic Encryption (FHE) allows to perform computations on encrypted data. The result of the computation remains encrypted, and only the owner of the secret key can decrypt it to see the final output.

#### Core APIs

- `keygen() -> (pk, sk, evk)`: Generate a public key (for encryption), a secret key (for decryption), and an evaluation key (to perform math on ciphertexts).
- `encrypt(pk, m) -> ct_m`: Transform message `m` into its corresponding ciphertext `ct_m`.
- `evaluate(evk, f, ct_m) -> ct_f(m)`: Evaluate function `f` over the ciphertext.
- `decrypt(sk, ct_f(m)) -> f(m)`: Reveal the result.

In the next scenario, Alice wants to run an LLM on their prompt `x` without revealing the prompt to the model provider. If the LLM were open source, Alice could run it locally. But even if the model is closed source, such as GPT 5.2, FHE allows, at least *theoretically*, for Alice to get their LLM output without having to disclose `x` to OpenAI.

#### Example: private AI inference

```
function LLMInference(user_input, model_weights)

// 1. Setup (run by Alice)
const { pk, sk, evk } = keygen(); // pk and evk are published

// 2. Encryption
const ct_x = FHE.encrypt(pk, x); // By the user
const ct_w = FHE.encrypt(pk, w); // By the model provider - `w` are the model weights

// 3. Evaluation (can be done by any untrusted server)
const ct_out = FHE.evaluate(evk, LLMInference, {ct_x, ct_w});

// 4. Decryption
const out = FHE.decrypt(sk, ct_out); // out = LLMInference(x, w)
```

In the next scenario, a user wants to prove that their encrypted value `m` falls within a specific range `[0, 999]` without revealing the input message `m` itself. While FHE is usually for outsourcing computation on private data, it is often combined with ZK-SNARKs to provide "proof of correct encryption" or "proof of plaintext properties".

#### Example: range proof on encrypted data

```
// The program logic
function EncryptAndRangeCheck(m, pk, expected_ct, min, max) {
    assert(m >= min);
    assert(m <= max);
    assert(expected_ct == FHE.encrypt(pk, m);)
}

ZK.setup(RangeCheck) -> pk, vk

// Prover
const proof = ZK.prove(pk, { min: 0, max: 999, pk: 0xabc, expected_ct: 0xaaa}, { m: 42 });

// Verifier
const isValid = verify(vk, { min: 0, max: 999, pk: 0xabc, expected_ct: 0xaaa}, proof);
// Result: true 
// The verifier is 100% sure the ciphertext they received
// is the result of correct FHE encryption of a value in the range [0, 999]
// but has no clue it's 42.
```

#### Tooling

Zama, OpenFHE

## 3. MPC

Multi-Party Computation (MPC) allows multiple parties to jointly compute a function over their inputs while keeping those inputs private. No single party ever sees the inputs of the others; they only see the final output. 

We are going to build MPC by adding a few APIs on top of the ones required for FHE that we just described. This is technically known as multi-party FHE (MP-FHE).

#### Core APIs

- `setup(n) -> (pk, sk_1, ..., sk_i, ..., sk_n, evk)`: Generate a public key (for encryption), `n` shares of the secret key (for decryption) for each `i`-th party, and an evaluation key (to perform math on ciphertexts)
- `local_decrypt(sk_i, ct_f(m)) -> f(m)_i`: Start from their secret key share each party obtains a share of the decrypted output
- `reconstruct(f(m)_1, ..., f(m)_n) -> f(m)`: By pooling together `n` shares of the decrypted output, the parties recover `f(m)`

In Yao's millionaire problem, three billionaries (A, B, C) want to establish who is richer without revealing their net worth.

#### Example: Yao's millionaire problem

```
// The program logic
function FindOutMax(x, y, z) {
    // Check if x is the largest
    if (x >= y && x >= z) {
        return 1;
    } 
    // If we reach here, x is not the largest. 
    // Now just check if y is larger than or equal to z.
    else if (y >= z) {
        return 2;
    } 
    // If neither x nor y are the largest, z must be.
    else {
        return 3;
    }
}


// 1. Setup (run jointly by A, B, C)
const { pk, sk_A, sk_B, sk_C, evk } = FHE.distributed_keygen(3);

// 2. Encrypt
const ct_netWorthA = FHE.encrypt(pk, netWorthA); // Executed by A
const ct_netWorthB = FHE.encrypt(pk, netWorthB); // Executed by B
const ct_netWorthC = FHE.encrypt(pk, netWorthC); // Executed by C

// 3. Evaluate (can be done by any party or even an external party)
const ct' = FHE.evaluate(evk, FindOutMax, {ct_netWorthA, ct_netWorthB, ct_netWorthC});

// 4. Local decryption
const max_A = FHE.local_decrypt(ct', sk_A) // Executed by A
const max_B = FHE.local_decrypt(ct', sk_B) // Executed by B
const max_C = FHE.local_decrypt(ct', sk_C) // Executed by C

// 5. Assemble the output
const max = FHE.reconstruct(whoSMax_A, whoSMax_B, whoSMax_C)
// They now found out who has the max net-worth 
// without knowing any of the other millionaires' net-worth
```

The setup I just described is fully secure since recovery only happens when all the `n` parties agree to. This sistem is *fully secure* because it guarantees any party that their net worth will never be reveled. This is the case because, in order to decrypt `ct_netWorthA`, all three decryption shares are necessary, but a rational party `A` would never provide their decryption share to the others. 

In practice, most of the existing instantiations of MPC [give up the full security guarantee to gain in efficiency](https://pse.dev/blog/why-we-cant-build-perfectly-secure-multi-party-applications-yet): an example is to set a threshold `t < n` of members that need to collaborate to recover a ciphertext. 

As an example, if we set `t = 2` for Yao's millionaire problem, only two parties, for example, B and C, are necessary to decrypt any ciphertext. Therefore, party A must trust that their millionaire friends, B and C, won't act maliciously.

#### Tooling

Zama fhevm, Phantom Zone

> Bonus point: Read this [article](https://machina-io.com/posts/unboxing.html) to explore, via the same API-oriented lens, more complex cryptographic primitives such as functional encryption (FE) and indistinguishability obfuscation (iO).