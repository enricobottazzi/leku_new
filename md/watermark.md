# Verifiable AI watermarking detection with zero-knowledge proof

When a text spreads online, a platform, journalist, researcher, or regulator may ask: did a particular AI provider's model generate this text?

AI watermarking is one possible solution.

A watermarking algorithm proceeds in two steps, both executed by the AI model provider:

```
Generate(secret_key, prompt) -> generated_text
Detect(secret_key, text) -> confidence
```

During generation, the provider receives the `prompt` from a user and returns a `generated_text`. This differs slightly from standard token generation because the token choice is subtly steered by a `secret_key`.

The `generated_text` should look like ordinary text. If the watermarking algorithm steers tokens too far from the "standard" distribution, an external observer can quickly reverse-engineer the algorithm and remove the watermark. Another risk is that the model's performance might suffer in the process.

After that, any user (requester) who sees online `text` might wonder whether it was AI-generated. To verify that, they share the `text` with the AI model provider, who runs `Detect` and returns a confidence level. The confidence level, expressed as a percentage, reveals how strongly the text matches that provider's watermark. 

Computerphile recently published a video on LLM watermarking that details a specific algorithm. In this article, I don't want to focus on the details of a specific algorithm, but on a broader problem that affects any state-of-the-art watermarking algorithm. 

Once a requester obtains a confidence level from the AI provider, they cannot independently verify how that number was obtained. Did the provider run the detector it promised to run, or did it simply return an answer that was convenient in that case?

A provider may face commercial, reputational, legal, or political pressure in a contested case. But it may also just be operationally lazy and prefer not to run a computationally expensive check. 

A system that matters for regulation, research, journalism, or disputes should not depend only on: "Trust us, we checked." Ideally, any requester should verify that the returned confidence level was computed honestly. 

A dummy solution would be to let the requester run `Detect` themselves. But this would force the AI provider to reveal their `secret_key`, which would make the `Generate` step fully reverse-engineerable.

This looks like an impossible problem to solve. This is where [zero-knowledge proofs](https://www.leku.ink/posts/cryptography_cheatsheet.html) enter. A zero-knowledge proof lets someone prove that a statement is true without revealing the secret information behind it. Simple intuition: prove you know a password without showing anyone the password.

In this case, the statement that the AI provider has to prove is:

> For this `text`, our `Detect(text, secret_key)` algorithm produced this `confidence` score

Without revealing `secret_key`.

So we can imagine the AI provider running a modified version of the `Detect` algorithm:

```
DetectWithProof(secret_key, text) -> confidence, proof
```

Crucially, the proof does not reveal any detail about the `secret_key` 

The requester can then locally verify the provider's honesty by running:

```
Verify(text, confidence, proof) -> accept / reject
```

But there's a caveat here: nothing binds the provider to use the same `secret_key` for both generation and detection. One other ingredient is needed first: a cryptographic commitment.

Before any generation runs, the provider must publish a commitment to its secret_key.

A commitment has two useful properties:

- Hiding: people cannot learn the secret key just by looking at the commitment.
- Binding: the provider cannot change its mind later. Once it has committed to a watermark key, it cannot credibly claim that the same public commitment corresponds to a different key.

To achieve verifiable AI watermarking detection, the flow is the following:

```
Commit(secret_key) -> commitment
Generate(secret_key, prompt) -> generated_text
DetectWithProof(secret_key, commitment, text) -> confidence, proof
Verify(text, confidence, proof, commitment) -> accept / reject
```

After the key is committed, the AI provider has to prove is:

> For this `text` and this `commitment` such that `Commit(secret_key) -> commitment`, our `Detect(text, secret_key)` algorithm produced this `confidence` score

The verification algorithm lets the requester verify this statement given a `proof` without revealing the `secret_key`.

The EU AI Act already establishes requirements around AI watermarking, while leaving technical implementation open.

A future guidance principle could also require that, when secret-key watermark detection is used to verify the provenance of a given text, providers can produce verifiable evidence for their detection results. 

Zero-knowledge proofs offer a neat way to do that: they do not make watermarking perfect, but they turn a provider's uncheckable assertion into a checkable cryptographic claim.
