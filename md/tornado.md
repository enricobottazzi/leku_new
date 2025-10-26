---
title: "You should not build Tornado Cash with FHE"
date: 2025-02-18T18:19:37+01:00
---

> Thanks to Auryn Macmillan for discussions and reviews.

![Screenshot 2025-02-13 at 08.53.26](https://hackmd.io/_uploads/H17-HXit1x.png)

[Rand Hindi](https://x.com/randhindi), CEO of Zama, argued in this [tweet](https://x.com/randhindi/status/1779832338228105726?s=61) about the difference between privacy applications built with ZK and with FHE. Tornado Cash-like systems (based on ZK), similar to Tor, are focused on anonymizing who is doing something (the identity/metadata) while the content of the transaction is visible on the public blockchain. FHE-powered applications, similar to Signal's end-to-end encryption, reveal the parties (metadata) involved in a transaction while the content of such transaction remains hidden. While this is a valid heuristic, there's much more to say about such differences. In this blog post, we will consider the specific case of [Tornado Cash](https://github.com/tornadocash) and compare it with an FHE version of Tornado Cash that we'll build. I assume that the reader is familiar with the main functionalites of ZK (prove and verify) and FHE (encrypt, perform addition and multiplication on encrypted data and decrypt).

## Tornado Cash

Let's first recap the design of the existing ZK-powered Tornado Cash, which will be after TC. TC is a mixer that allows the transfer of ETH and other tokens from address A to address B while hiding the link between the two accounts. It works as follows: 

1. Create a secret, hash it into a commitment, and send x ETH with the commitment to the TC Smart Contract (SC). Upon TX confirmation, the commitment is added as a leaf to the Merkle tree, accumulating all the TC depositors. Note that this operation is performed by address A 
2. Wait some time ...
3. To withdraw the money, submit a ZK proof to the TC SC with the address B to which you wish to transfer x ETH. The proof is proving that:
     -  You know the secret behind a commitment in the depositors' Merkle tree
     -  You haven't withdrawn before via the so-called nullifier
4. On proof verification, x ETH is transferred from TC SC to address B. Note that the proof doesn't reveal any detail about the identity of address A.

Notably, the transaction at step 3 could be formally submitted by a [relayer](https://x.com/_jefflau/status/1468065481324392453?s=61), whose role is to submit proof on behalf of address B, which might not have any ETH to pay for the gas fees.

## FHE-powered Tornado Cash

I don't know whether such an application exists. Here, I'm going to present a naive way in which I would design it. Notice that a cryptographic scheme, like El-Gamal, that supports additive homomorphism should be enough. I won't argue about the efficiency of performing such operation natively on Ethereum because you can always imagine an L2 rollup, similar to [Fhenix](https://www.fhenix.io/), that bears the computation burden. The contract stores a mapping of type `address -> enc(amount).`

The application works as follows:

1. Send an initial deposit of y ETH from address A to the FHE-TC SC. Upon transaction confirmation, the contract is going to update the deposit mapping as follows: 
    `address A -> += enc(y)`
2. To send x ETH from address A to address B, submit a transaction that includes: 
    -  the address of the designated receiver 
    -  the encrypted amount `enc(x)` that you wish to send
    -  a ZK proof that `x` is less or equal to your current deposit `y`. You can use [Greco](https://github.com/privacy-scaling-explorations/greco) for that
4. On proof verification, the mapping is updated by leveraging the additive homomorphism of the employed scheme as follows: 
    `address A -> -= enc(x)`
    `address B -> += enc(x)`
    
## Comparison

#### Sender-receiver anonymity

Sender anonymity is guaranteed if an external actor cannot identify the address A sending x ETH. Similarly, receiver anonymity is guaranteed if an external actor cannot identify the address B receiving x ETH. 

TC accomplishes it with a few caveats. The addresses of the TC depositors are public, so the sender's anonymity is limited within that set of addresses. The degree of anonymity increases with the number of TC depositors. Further chain analysis attacks based on the timing of the deposit and the withdrawal can be used to deanonymize the link between the sender and the receiver. The identity of the receiver is public.

In FHE-TC, both the identity of the sender and the receiver are public, as their entries in the mapping get updated after a transfer. Interestingly, if the transaction at step 2 is sent to the smart contract through a relayer, the mapping update would not necessarily disclose who is the receiver and who is the sender. This principle can be stretched to the limit by updating all the entries by adding an encryption of 0 to their balance every time a token transfer is performed. Similar to differential privacy, this strategy would guarantee sender-receiver anonymity with the cost of a considerable performance overhead.

#### Amount privacy

That is, the guarantee that the withdrawn amount x of the transaction is not revealed to any external actor. 

Legacy TC doesn't support this feature and consists of different mixer pools for fixed amounts such as 1ETH, 10ETH, 100ETH. Nevertheless, more advanced systems like [Railgun](https://www.railgun.org/): once deposited into the Railgun pool, tokens can move in arbitrary amounts between arbitrary parties in a way that is completely opaque thanks to its UTXO private transactions model supporting amount privacy.

FHE-TC also supports amount privacy since the amount being transferred is encrypted. Note that for the FHE case, the amount deposited to the smart contract is public. It follows that if the first action performed by the user is an outbound transfer, the amount is known to be less than the initial deposited amount.

#### Security

This is one of the most overlooked aspects when comparing ZK-based architecture vs FHE-based ones. In particular, I'm concerned about the possibility of breaking the privacy that the application is supposed to guarantee. 

In any ZK system, the zero-knowledge property of any proof is guaranteed even if the initial trusted set-up is attacked. By contrast, FHE-TC needs to rely on a committee managing shares of the decryption key, which can silently [collude](https://mirror.xyz/privacy-scaling-explorations.eth/nXUhkZ84ckZi_5mYRFCCKgkLVFAmM2ECdEFCQul2jPs) and decrypt any information related to users' balances and transfers.

It is worth noting that if an adversary gains access to *all* the secret wastes used during the initial trusted set-up, they can use it to create valid-looking proofs even for false statements, breaking the soundness of the system. This is worse than breaking the privacy of the users. Since both TC and FHE-TC rely on ZK proofs, they are equally affected by this potential attack.

#### Bonus point: complexity 

FHE's logic is generally more straightforward for people to understand. A [demo](https://www.loom.com/share/f145592ad2974613b8669f8f38cc98a4) from Zama illustrates how a developer can take any existing smart contract logic and change data types into encrypted ones. In contrast, ZK app often requires builders to develop off-chain data structures (such as Merkle trees) and carefully manage commitment updates on chain based on some proof-verification logic.

## Conclusion

The main takeaway from this article is that building Tornado Cash-like applications with FHE doesn't make much sense as it underperforms the corresponding solely ZK-based construction over almost all the axes. The meta intention of this post is not to discredit FHE but to raise awareness of the risk of spreading FHE over all the applications. Indeed there is a broad set of powerful multi-party [applications](https://www.leku.blog/beyond-zkml/) in which the computation involves aggregating private inputs from many parties that cannot be built with ZK-only and require FHE.