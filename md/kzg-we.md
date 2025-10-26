---
title: "Notes on Extractable Witness Encryption for KZG Commitments and Efficient Laconic OT"
date: 2024-09-03T12:24:37+02:00
math: true
---

### Core Resources

- [Paper](https://eprint.iacr.org/2024/264)
- [Youtube presentation of the paper](https://youtu.be/81Hq7Ij94vE?si=G1CO9m3Sl1nw6ukB)

### Witness Encryption (WE) 

First of all, what is Witness Encryption?

You can compare it with a normal public encryption scheme. What you would normally do is to encrypt under a public key. You encrypt a message towards a public key. The encryption returns a ciphertext that can only be decrypted using the secret key that corresponds to the public key.

Instead, with WE, a message is encrypted towards a statement. $x$ is a statement, and $w$ is a valid witness for that statement. In witness encryption, we replace the public key with the statement and the secret key (or decryption key) with the witness. The formal condition is that the $(x, w)$ is a valid NP relation in R. In other words, $w$ must be a valid witness for the statement $x$ is order to allow decryption.

![Screenshot 2024-08-04 at 11.59.04](https://hackmd.io/_uploads/ryjFCP2YC.png)

This kind of witness encryption for any NP relation is only theoretical at this point. It can be constructed from indistinguishability obfuscation or non-standard lattices assumption, but it is not practical or efficient. The paper suggests building WE for a specific set of NP relations, namely KZG commitments.

### WE for KZG commimtents

Check this [blog post](https://scroll.io/blog/kzg) from Scroll for a better understanding of KZG commitments.

KZG is a polynomial commitment scheme. Here, the polynomial is $f$. Remember that you can pack a lot of information into a polynomial! 

![Screenshot 2024-08-06 at 14.09.22](https://hackmd.io/_uploads/Syabe4150.png)

The high-level idea of WE for KZG commitments is to encrypt a message towards a triple $com, \alpha, \beta$ where $\alpha$ is a point and $\beta$ is the required evaluation at that point. Someone that *knows* a correct opening proof $\pi$ for that triple should be able to decrypt that message. 

Performing WE based on KZG like that is not secure (min 9:40 of the YT video). More on that in Witness Encryption vs Extractable Witness Encryption section of this article. The authors, therefore, focus on the notion of Extractable Witness Encryption.

To construct such a scheme, the authors start by describing a simpler algorithm: Extractable Witness KEM for KZG, which is simpler but very similar to WE. But first of all, what is even a KEM?

KEM stands for Key Encapsulation Mechanism, this is commonly used to securely exchange a symmetric key between two parties over a public insecure channel. There are two algorithms:

{{<rawhtml>}}
$$
\begin{align*}
\text{Encap}(pk) &\rightarrow \text{k, ct} \\
\text{Decap}(ct, sk) &\rightarrow k
\end{align*}
$$
{{</rawhtml>}} 


For example, the sender will generate the ciphertext $ct$ that encapsulates the key $k$ using the receiver's public key $pk$. The sender can now send the ciphertext over any public channel. The receiver can then decapsulate the key from the ciphertext with their secret key $sk$. After the decapsulation, $k$ can be used as a symmetric key to guarantee secure communication between the two parties.

KEM is very similar to regular asymmetric encryption. The main difference is that in asymmetric encryption, you specify the message you want to encrypt, while in KEM, the thing that you want to encrypt (the key $k$, in practice) is randomly generated as part of the algorithm.

Similarly, the difference between Witness KEM and regular WE is that in the first case, we witness encrypting a random key $k$, while in WE, we encrypt a specific message $m$.

![Screenshot 2024-08-04 at 12.35.28](https://hackmd.io/_uploads/HyEzvdhYA.png)

Using this scheme, only the person able to generate the valid opening proof can decapsulate the key $k$.

Once we have this basic construction, obtaining witness encryption is pretty easy since we can use the encapsulated/decapsulated key $k$ into a symmetric encryption scheme to encrypt arbitrary messages $m$.

![Screenshot 2024-08-06 at 11.48.21](https://hackmd.io/_uploads/ByQZyfy5A.png)

### Oblivious Transfer

This is a traditional OT between Alice and Bob. Informally, OT should guarantee Bob to receive from Alice the message corresponding to his bit $m_b$ without leaking to Alice the information about which message was requested.

![Screenshot 2024-08-04 at 12.55.53](https://hackmd.io/_uploads/HytRo_3Y0.png)

In the traditional version, each message requires two rounds of communication between Alice and Bob

The Laconic version of OT makes the scheme more efficient. In particular, Bob compresses all his $n$ bits into a dictionary and sends the digest of the dictionary $D$ to Alice. In this way, a transfer of $n$ messages between Alice and Bob requires constant communication rounds (namely 2). We kind of batch all the Oblivious Transfers together.

![Screenshot 2024-08-04 at 13.02.42](https://hackmd.io/_uploads/B1mOp_2KR.png)

WE for KZG is used to compress the dictionary Bob sent in the first place. After receiving the commitment $com$ from Bob, Alice will encrypt their contradictory messages under the KZG triples. For example, she will encrypt ${m_0}^1$ under the opening of the commitment to $0$ at the point $1$ and the message ${m_1}^1$ under the opening of the commitment to $1$ at the point $1$. Bob will only be able to decrypt the message that corresponds to the bit he commited to at position $1$ of the dictionary by providing a valid opening proof.

![Screenshot 2024-08-04 at 13.04.47](https://hackmd.io/_uploads/SJWg0_3YR.png)

Note, once again, Alice doesn't get to know which opening verifies as she is not involved in the $Receive$ funtion that can be run independently by Bob. 

### Witness Encryption vs Extractable Witness Encryption

This is more of a nerd snipe of mine, which is probably not required for engineers trying to understand Witness Encryption. 

Let's start with the definition of Witness Encryption provided by [GGSW13]. You have a set of NP relations $R = \set{(x, w) : M_R(x, w) = 1}$. These are sets of relations between a statement $x$ and witness $w$ that you can efficiently check if the relation holds via an algorithm $M_R$. This is similar to the definition of zero-knowledge proof. According to [OB21], a proof for a relation $R$ is a protocol between a prover $P$ and an efficient verifier $V$ by which $P$ convinces $V$ that $\exists{w} : M_R(x,w) = 1$ where $x$ is a defined a statement, and $w$ is a witness for that statement. 

For WE, we also define a language $L$ related to this NP relation that contains all the $x$ such that it exists a witness $w$ such that the tuple $(x, w)$ is in the relation $R$. 

$$L= \set{x : \exists{w}. (x, w) \in R}$$

We can build a Witness Encryption protocol from this standard definition of an NP language $L$ (with corresponding witness
relation $R$). The encryption algorithm will take the statement $x$ as input (together with a message $m$) and return a ciphertext, while the decryption algorithm will take the witness $w$ as input (together with the ciphertext) and return the message $m$. 

We now need to define the notions of **correctness** and **semantic security** for the scheme

![Screenshot 2024-08-06 at 15.45.48](https://hackmd.io/_uploads/HJKoUB1qC.png)

The correctness property guarantees that if the tuple $(x, w)$ is a valid relation, the decryption algorithm will return the correct message $m$. 

![Screenshot 2024-08-06 at 15.47.49](https://hackmd.io/_uploads/BkemDHycR.png)

The semantic security property guarantees that if $x$ is not in the language $L$ and if I have two different messages $m_0$ and $m_1$ encrypted under a statement $x$ that is not in the language, the generated ciphertexts are computationally undistinguishable. Under this property, nobody should be able to tell whether these ciphertexts correspond to an encryption of $m_0$ or $m_1$.

This second security property holds only if $x \notin L$. If $x$ is in the language $L$, this property doesn't hold anymore, i.e., ppl can break the semantic security and learn the message behind the ciphertext. 

So now, let's go back to our attempt at building witness encryption, which started with the KZG commitment scheme. 

In that case, the statement $x$ equals the triple $(com, \alpha, \beta)$, and the witness is the opening proof $\pi$. A statement is in the language if an opening proof exists such that the verification algorithm returns true.

![Screenshot 2024-08-06 at 16.02.29](https://hackmd.io/_uploads/SJW99Skq0.png)

The problem is that for any instantly valid triple, there **exists** an opening; therefore, $x$ is always in the language. This is a problem because, according to the notion of WE defined by [GGSW13], this wouldn't guarantee semantic security (i.e., that the message is hidden). In other words, under this KZG-based WE scheme, everyone would be able to decrypt the message as long as the triple used as statement $x$ for encryption is in the language $L$. Instead, we want the message to be decryptable only for those who know a valid opening proof $\pi$ for that statement.

To do so, we add the notion of extractability to our WE scheme, as introduced by [GKP+13]. This says that if an adversary can break semantic security for a statement $x$, an extractor can extract the witness $w$ for $x$. This is cool because we kind of extend the semantic security notion of normal WE also to $x$ that are in the language, which is the case for our KZG-based scheme. 

That's why the authors focus their efforts on building an EWE scheme. Also, most of the paper's content is dedicated to proof that this scheme is actually extractable, which is beyond the scope of our research. 

Note that at 1:02:00 of [presentation](https://youtu.be/81Hq7Ij94vE?si=G1CO9m3Sl1nw6ukB), Nils mentions a possible 2-round Witness Encryption scheme for Arbitrary Statements based on zkSNARKs. In particular, he specifies that this is not an Extractable Witness Encryption but a *normal Witness Encryption*. Why is that the case? At 0:05:30 in the presentation, he claims that the semantic security of WE holds when you are working with a language in which it is hard to decide whether $x$ is in the language or not and I think this applies to zkSNARKs.

### Conclusions

After reading the paper, the main questions that I’ve been asking myself is if there are other applications that we can built other than Laconic Oblivious Transfer out of the Extractable WE for KZG commitments. 

One of the most interesting application is to reduce round of interactions in multi-party applications and, more specifically, private set intersections (PSI) protocols. Ideas in this direction have been proposed by Cursive team, for [job matching](https://x.com/viv_boop/status/1823078309758120090?s=61), by Ingonyama, for [fog of war games](https://medium.com/@ingonyama/cryptographic-fog-of-war-9b8785ba744a) and by Yiğit Kılıçoğlu, for [dark chess](https://docs.google.com/document/d/1NKlXGp6SA32hZcv-NY0PsTs4kYVaMOUi36wuCUvgoPs/edit).

Another compelling use case is to built 2-round Witness Encryption scheme for Arbitrary Statements based on zkSNARKs as mentioned by the author of the paper at 1:02:00 of his [presentation](https://youtu.be/81Hq7Ij94vE?si=G1CO9m3Sl1nw6ukB) but I'm not sure whether a) this is anywhere useful b) WE is overkill.

### References 

- [GGSW13](https://eprint.iacr.org/2013/258.pdf)
- [OB21](https://eprint.iacr.org/2021/1530.pdf)
- [GKP+13](https://people.csail.mit.edu/nickolai/papers/goldwasser-we.pdf)
