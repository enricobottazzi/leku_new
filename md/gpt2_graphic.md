# GPT2, graphically spelled out

This week I went through the *Let's build GPT2* [tutorial](https://www.youtube.com/watch?v=kCc8FmEb1nY) from Andrej Karpathy. Andrej does an amazing job in building from scratch a transformer model piece by piece (read layer by layer) and use that to train a dummy GPT2 model. This article provides a graphical complementary to the tutorial, which mainly focuses on the python code. More specifically, I start from the Transformer architecture figure from the seminal *Attention Is All You Need* [paper](https://arxiv.org/pdf/1706.03762) and enanche it with an interactive view of the matematical artifcats (vectors or matrices) for:
- input/output of each layer which can be viewed by clicking on the arrows between layers
- parameters stored inside each layer which can be viewed by clicking over the quadrant of each layer

The remaining sections are dedicated to a more detailed description of the matematical operations done at each layer and to the difference between training and inference phase with respect to the transformer architecture.

The architecture described in this article refers to the one deployed up to 01:37:49 in the youtube tutorial. For the sake of simplicity we don't consider the input of the transformer to come in batch (`batch_size = 1`). Furthermore, the self-attention layer to be single-headed (`n_head=1`). In other words, we disregard the optimization performed by Andrej at 01:21:59. 

## Interactive transformer architecture

The interactive figure below describes a forward pass of a decoder transformer-based model. To map it to Karpathy's code, this refers to the `BigramLanguageModel.forward` function in the case in which no `targets` input is provided. The input to the token embedding is a vector of token `idx = token_id_0, token_id_1, ... token_id_block_size-1`, while the input to the position embedding is a vector of positions `pos = 0, 1, ..., block_size-1`. The output is a `logits` matrix, which maps each input token to a `(1 x vocab_size)` vector that associates an unnormalized score for next token prediction.

By setting `vocab_size=65`, `n_embd=32`, `block_size=8` and `N=3`, the architecture described in the figure results in the following total parameters count

| Component | Layer | Parameter | Shape | Count |
|-----------|-------|-----------|-------|------:|
| **Embeddings** | Token embedding | weight | 65×32 | 2,080 |
| | Position embedding | weight | 8×32 | 256 |
| **Block ×3** | LayerNorm 1 | weight + bias | 2×(1×32) | 64 |
| | Self-Attention (K, Q, V) | weights | 3×(32×32) | 3,072 |
| | LayerNorm 2 | weight + bias | 2×(1×32) | 64 |
| | FeedForward Linear 1 | weight + bias | (32×128)+(1×128) | 4,224 |
| | FeedForward Linear 2 | weight + bias | (128×32)+(1×32) | 4,128 |
| | | **Block subtotal** | | **11,552** |
| | | **×3 blocks** | | **34,656** |
| **Output** | Final LayerNorm | weight + bias | 2×(1×32) | 64 |
| | LM Head | weight | 32×65 | 2,080 |
| | LM Head | bias | 1×65 | 65 |
| | | **Total** | | **39,201** |

An equivalent model instance can be access from this repositiory (TO ADD). Running `python model.py` logs the total number of parameters of the model matching the total calculated above.

## Layers

This section describes in more detail the operation performed inside each layer with focus on the ones that were overlooked in Karpaty's tutorial. 

- Feed forward layer 

### Embedding layers

Both embedding layers (`token_embedding_table` and `position_embedding_table`) are **lookup tables**. The former maps each token id (for a total of `vocab_size`) to a vector of size `n_embd`. The latter maps each position id (for a total of `block_size`) to a vector of size `n_embd`. They don't perform any matrix multiplication. Given an input vector of shape `(block_size x 1)`, it replaces each integer with the corresponsing row producing a matrix of shape `(block_size x n_embd)`

### Addition layer

Simply element-wise addition between two input vectors. No parameters are stored there.

### Layer norm

Described by Karpathy at 01:32:51.

### Self-attention layer

Described by Karpathy at 01:02:00.

### Feed-forward layer

The feed-forward layer is a small two-layer network applied independently to each row. It chains: a linear layer (see below) that expands from `n_embd` to `4 * n_embd`, a ReLU activation (which simply replaces negative values with zero — no learned parameters), and a linear layer that projects back from `4 * n_embd` to `n_embd`. Both linear layers here are instantiated with bias. The input and output shapes are both `(block_size, n_embd)`.

### Linear layer

A linear layer takes an input matrix `X` of shape `(block_size, in_features)` and projects it to shape `(block_size, out_features)`: the number of rows stays the same, while each row is independently transformed from size `in_features` to size `out_features`. It stores a weight matrix `W` of shape `(in_features, out_features)` and, optionally, a bias vector `b` of size `out_features`. The output is computed as `output = X @ W + b` (or just `X @ W` when there is no bias). Some linear layers in this architecture are instantiated without bias (e.g. the `key`, `query`, `value` projections inside the self-attention layer).

## Training vs inference

Both the training and inference phase start with a forward pass through the transformer architecture. One difference involves the input vector of the forward pass. During training, the `idx` input vector is sampled from the training data set. During inference, the `idx` vector is composed of tokens either provided by the user or previously generated by the transformer itself. The second, more fundamental, difference involves what to do after the forward pass is complete and the `logits` are obtained. 

During training phase, the logits for each token are compared with the expected next token (from `targets`) to compute the loss. The overall loss is calculated as mean of each token's loss and backpropagated through the transformer architecture to update the parameters to reduce the loss. Note that all `block_size` predictions are produced in a single forward pass: this is possible because the self-attention layer applies a **causal mask**: when computing the representation at position `t`, the mask zeroes out any contribution from positions `t+1, ..., block_size-1`. Without it, the model could "cheat" by simply reading the next token from its own input and learn nothing useful.

During inference phase, only the logits for the last token are extracted. These scores are then normalized via Softmax to produce a probability distrution which is eventually used to sample the next token, which is further appended to the `idx` vector.