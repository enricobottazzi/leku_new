---
title: "Ouragan, a Tornado Cash offramp"
date: 2024-04-15T15:19:08+02:00
publishdate: 2024-04-15
lastmod: 2024-04-15
math: true
description: Ouragan allows a user to use the mixing property of TC without passing through the monitored `withdraw` function
---

> You can leave comments on the hackMD version of this document [here](https://hackmd.io/@Leku/Bkj8EC9k0).

<figure align="center">
  <img src="https://github.com/enricobottazzi/leku/blob/main/assets/ouragan.png?raw=true">
</figure>

On the 8th of August 2022, the US Department of Treasure [sanctioned](https://home.treasury.gov/news/press-releases/jy0916) the "*Notorious Virtual Currency Mixer [Tornado Cash](https://github.com/tornadocash)*." As a consequence of this, Exchanges and Stablecoin providers [started](https://www.theblock.co/post/162172/circle-freezes-usdc-funds-in-tornado-cashs-us-treasury-sanctioned-wallets) [blacklisting](https://www.coindesk.com/business/2022/08/11/crypto-exchange-dydx-blocked-accounts-that-received-even-small-amounts-from-tornado-cash/#:~:text=Cryptocurrency%20exchange%20dYdX%20said%20it,by%20the%20U.S.%20Treasury%20Department.) any address linked to Tornado Cash (TC) from their services. Specifically:
- Addresses who [deposited](https://github.com/tornadocash/tornado-core/blob/master/contracts/Tornado.sol#L55) to TC 
- Addresses who were a [withdrew](https://github.com/tornadocash/tornado-core/blob/master/contracts/Tornado.sol#L76) `recipient` from TC

Funnily enough, according to the logic of the contract, the `recipient` does not need to be the one performing the withdrawal. Because of that, people could *sacrifice* 0.1 ETH and designate their sworn enemy as a recipient address to *gift* them with a ban. 

As a consequence of the sanctions, the traffic of TC [declined by 85%](https://www.trmlabs.com/post/tornado-cash-volume-dramatically-reduced-post-sanctions-but-illicit-actors-are-still-using-the-mixer).

[Ouragan](https://github.com/Jubzinas/Ouragan) is a project built during Lambda ZK week in Paris 2023 together with [Giorgio](https://twitter.com/jubzinas) and [Pierre](https://twitter.com/xyz_pierre) to allow users to deposit into Tornado Cash and withdraw without incurring in any of the sanctions above. 

Let us dive into the tech! 

### Intro to Tornado Cash

Here is a [brief introduction](https://twitter.com/_jefflau/status/1468065457190350850) to the TC technology. [Here](https://www.rareskills.io/post/how-does-tornado-cash-work) is a more extended one. The main thing that we are worried about is that the only way to move a deposit out of TC is to pass through the [`withdraw`](https://github.com/tornadocash/tornado-core/blob/master/contracts/Tornado.sol#L76) smart contract function. This function requires the user to provide a ZK proof that they know the `secret` and `nullifier` behind a `commitment` part of the depositor Merkle Tree.

However, this function is monitored by financial institutions that are ready to ban every associated address. For a US citizen or someone dealing with US-based financial services, using TC for privately seeding a wallet is a no-go. 

Alternatively, users could leverage other existing mixers that are not yet monitored or just fork their version of TC. The problem with such solutions is twofold: 

- If the alternative mixer has little to no activity, the anonymity set of the depositors is so tiny that this can nullify the address mixing property
- If the alternative mixer gets activity, it will also draw the attention of the sanctionator, and this will likely incur sanctions similar to what happened to TC.

Given the state of the art, using TC or any of its clones is a risky decision for any US-based user who wants to privately seed a wallet.

### Ouragan

At its core, Ouragan allows a user to use the mixing property of TC without passing through the monitored `withdraw` function. Instead, they (the `seller`) would deposit to TC and sell their deposit for a discount to a user (the `buyer`) who is willing to take the risk of withdrawing from TC. The buyer is likely a user not afraid of US sanctions because they are not a US citizen or not connected to US financial services. 

Ouragan is designed to never directly interact with or be linkable to the TC contract. A party monitoring the TC contract shouldn't be able to tell whether a withdrawal has been performed by a "legit" TC depositor or by a `buyer` of someone else's deposit. 


<figure align="center">
  <img src="https://github.com/enricobottazzi/leku/blob/main/assets/ouragan-scheme.png?raw=true" >
  <figcaption>Ouragan scheme</figcaption>
</figure>

#### Step 1

Alice wants to use TC to seed a wallet with $1$ ETH privately, but she is afraid of incurring in sanctions. Alice is ok to pay a premium of $0.1$ ETH for the service. In order to do that, Alice performs an `ask` to an instance of the Ouragan Smart contract, attaching a fresh new public key and the amount she is willing to pay.

#### Step 2

Bob is ok to accept the deal. In order to accept, he has to:
- create a `secret` and a `nullifier` and obtain a `commitment` by hashing those
- create a shared secret between him and Alice and use this to encrypt the commitment 
- places an `order` on the instance of the Ouragan smart contract by sending $0.9$ ETH (the sum asked by Alice) to the smart contract along with the encrypted commitment and his fresh new public key

#### Step 3

Alice, preferably with a wallet not linked to the one used for the ask function, can:
- fetch Bob's public key and retrieve the shared secret to decrypt Bob's commitment
- deposit $1$ ETH to TC by attacching Bob’s Commitment

#### Step 4

In order to unlock the $0.9$ ETH locked in the Ouragan smart contract instance, Alice must submit a ZK proof that the commitment provided by Bob inside the `order` has been correctly added to the TC Merkle Tree. Once the smart contract verifies this proof, Bob's deposit is unlocked to Alice.

#### Step 5

Bob can now withdraw $1$ ETH from TC by performing the notorious `withdraw` function and attaching a ZK proof that he knows the `secret` and the `nullifier` behind a `commitment` which is stored inside TC's Merkle Tree. Note that Bob is the only one able to perform the withdrawal since he knows the secrets behind it and is, therefore, able to generate the required ZK proof.

### Achievements

Let us put ourselves in the shoes of a regulator monitoring the TC Smart Contract. The withdrawal function is performed by the address `Bob1`. The default property of TC guarantees that the address that performs the withdrawal is not linkable to the depositor address `Alice1`. The regulator has now learned that a protocol named Ouragan provides users with an alternative way to offramp from TC. They want to determine if the withdrawal performed by `Bob1` is a "legitimate" withdrawal or a withdrawal resulting from an Ouragan trade. In the former case, `Bob1` is the only user to ban. In the second case, there is an additional mysterious user to ban. The goal of the regulator is to find out this mysterious user (in this case, `Alice0`) and emit a ban on them.

The main issue for the regulator would be to **discover the contract** that managed the trade between Alice and Bob. The only information they have is the existence of a depositor user `Alice1` with a `commitment` and a withdrawal user `Bob1`. There's no trace of such information in the Ouragan smart contract used by Alice and Bob, and therefore, such data can not be used to perform any meaningful on-chain analysis.

Furthermore, a new instance of the Ouragan smart contract can be deployed to handle a single trade. In such an extreme case, Alice and Bob can agree on the trade off-chain and then deploy a new instance of the Ouragan smart contract, of which they are the only ones who know the address, and perform the trade using such instance. 

In such a scenario, the only way for the regulator to discover the existence of such an instance of a Ouragan smart contract (and ban `Alice0`) is if Bob confesses it to them.

### Conclusions

Ourgan provides a clever trick for users to perform a sanction-less offramp from Tornado Cash. The protocol was built over a weekend as part of a hackathon, and its security is not audited. It has some open [issues](https://github.com/Jubzinas/Ouragan/issues) and known [limitations](https://github.com/Jubzinas/Ouragan?tab=readme-ov-file#architecture-limitations). 
