# The Einstein test but for post-training

Demis Hassabis [recently spoke](https://youtu.be/huAwz_BR8WM?t=795) about the [Einstein Test](https://cacm.acm.org/opinion/the-einstein-test-a-test-of-ais-ability-to-generate-transformative-science/): train an LLM on human knowledge with a cutoff at 1914 and see if it can "rediscover" general relativity (1915). The result would tell us whether AI can truly generate transformative science. 

The biggest practical issue is data contamination: how do we ensure the LLM never encounters any data after 1914 during training and inference? Data from the past have two issues. First, they are scattered and hard to timestamp accurately. Second, there might not be enough of them to sufficiently train the LLM to become intelligent enough to derive general relativity. 

If the result of the experiment is negative, people will argue that the results don't reflect the state of the art in LLMs because the experiment uses data-handicapped models. 

If the result of the experiment is negative, people will complain about the methodology and suspect that the model was somehow pushed towards the discovery. Either by having accessed post 1915 data or because of the bias introduced by the testing team tasked to provide the model "with initial guidance [...] to address the unsolved issues faced by the scientists of that time."

But maybe the core principle of testing retrospective scientific-discovery ability can be repurposed from eval to post-training.

Let's move our $t_0$ from 1914 to our days. The good thing about today is that everything is timestamped. [Internet archive](https://web.archive.org/) stores daily snapshots of each internet page. GitHub has version control for repositories and packages. Old training corpora stored by frontier labs can act as almost-complete human knowledge available as of DDMMYYYY. 

Since the data is already there, why don't we use this time sequence to elicit the capacity to generate transformative science during training? 

Here's a suggested (intentionally underspecified) pipeline to turn the Einstein test from a one-off eval to a repeatable post-training objective: 

Given the time sequence of human knowledge at various cutoffs $[K_{t_0}, ..., K_{t_N}]$, for each $t_i \in [t_0, ..., t_{n-1:}]$

1. Let the model ingest $K_{t_i}$
2. Construct a frontier card $\Delta_{t_i \rightarrow t_{i+1}}$, that describes the scientific breakthorughts that happened from $t_i$ to $t_{i+1}$. Do not show it to the model until step 4.
3. Ask the model to predict $\Delta_{t_i \rightarrow t_{i+1}}$
4. Score the difference between the prediction and reality and use the score as a reward signal 
5. Advance the clock
