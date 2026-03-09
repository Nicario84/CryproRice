# CryptoRice — Private Voting DApp

A decentralized private voting system built with Solidity, JavaScript, and Python. Votes are encrypted client-side using ElGamal encryption before being submitted on-chain, ensuring that individual vote choices are never revealed publicly. Only the election authority holding the private key can decrypt and tally votes after the voting period ends.

## Architecture

```
keygen.py → generates ElGamal public/private keys
                ↓
Frontend (app.js) encrypts vote with public key → submits to PrivateVoting.sol on Sepolia
                ↓
export_ballots.py → reads encrypted ballots from the contract → voters.json
                ↓
tally_votes.py → decrypts with private key → tally_result.json → publishFinalResults() on-chain
```

## Project Structure

```
├── contracts/
│   └── PrivateVoting.sol          # Solidity smart contract (Sepolia)
│
├── frontend/
│   ├── index.html                 # Voter UI
│   ├── style.css                  # Styling
│   ├── app.js                     # MetaMask + ElGamal encryption + contract interaction
│   └── public_key.json            # Public key for vote encryption (auto-loaded)
│
├── crypto/
│   ├── keygen.py                  # Generate ElGamal keypair
│   ├── encrypt_vote.py            # (Unused — encryption is done in the browser)
│   ├── export_ballots.py          # Export encrypted ballots from the contract
│   └── tally_votes.py             # Decrypt and count votes off-chain
│
├── data/
│   ├── public_key.json            # ElGamal public key (p, g, y)
│   ├── private_key.json           # ElGamal private key (p, g, x) — authority only
│   ├── voters.json                # Exported ballots from the contract
│   └── tally_result.json          # Final decrypted vote counts
│
└── README.md
```

## How It Works

### 1. Key Generation (Authority)

Run once to generate the ElGamal keypair:

```bash
python3 crypto/keygen.py
```

This creates `data/public_key.json` and `data/private_key.json`. The public key is also copied to `frontend/public_key.json` so the frontend can auto-load it.

**Parameters (demo):** prime p = 467, generator g = 2. This is intentionally small for learning purposes — not production-grade.

### 2. Deploy the Smart Contract

1. Open [Remix](https://remix.ethereum.org)
2. Paste `contracts/PrivateVoting.sol`
3. Compile with Solidity 0.8.20+
4. Set Environment to **Injected Provider - MetaMask** (Sepolia)
5. Deploy with constructor parameters:
   - `_title`: `"Class Election"`
   - `_candidateNames`: `["Alice","Bob","Charlie"]`
   - `_durationSeconds`: `3600`
   - `_requireApproval`: `false`
6. Copy the deployed contract address
7. Update `CONTRACT_ADDRESS` in `frontend/app.js` and `crypto/export_ballots.py`

### 3. Start the Frontend
**Option A — Local server:**

```bash
cd frontend
python3 -m http.server 8000
```

Open http://localhost:8000 in a browser with MetaMask installed.

**Option B — Hosted page:**
You can also access the frontend directly at: https://u236098.github.io/VOTEPAGE/

### 4. Vote

1. Click **Connect MetaMask** (must be on Sepolia)
2. Click **Load Election** — contract info and candidates load automatically
3. Enter a candidate number (e.g. 1 for Alice, 2 for Bob)
4. Click **Encrypt Vote** — ElGamal encryption runs in the browser
5. Click **Submit Vote** — the encrypted ballot is sent to the contract

### 5. Export & Tally (Authority — after voting ends)

Export encrypted ballots from the contract:

```bash
python3 crypto/export_ballots.py
```

This will only work after the voting period has ended. It saves all encrypted ballots to `data/voters.json`.

Decrypt and count the votes:

```bash
python3 crypto/tally_votes.py
```

This outputs the final counts (e.g. `[0, 1, 0]`) and saves them to `data/tally_result.json`.

### 6. Publish Results (Authority)

In Remix, call `publishFinalResults` on the deployed contract with the counts array (e.g. `[0,1,0]`).

After publishing, anyone can click **View Results** on the frontend to see the winner and vote counts.

## Smart Contract Features

- **Election lifecycle**: Setup → Voting → Awaiting Results → Closed
- **Encrypted ballots**: Votes stored on-chain as opaque bytes — the contract never sees plaintext choices
- **Voter approval toggle**: Optional whitelist mode (`requireApproval`)
- **One vote per address**: Enforced on-chain
- **Time-locked voting**: Configurable duration set at deployment
- **Result validation**: Total counted votes cannot exceed total voters

## ElGamal Encryption

The system uses ElGamal encryption to protect vote privacy:

- **Encryption** (browser): $c_1 = g^k \bmod p$, $c_2 = m \cdot y^k \bmod p$
- **Decryption** (authority): $m = c_2 \cdot (c_1^x)^{-1} \bmod p$

Where $m$ is the candidate number, $k$ is a random value, $y$ is the public key, and $x$ is the private key.

## Dependencies

- **Frontend**: ethers.js v6 (loaded from CDN), MetaMask browser extension
- **Python**: `web3` (for export_ballots.py only)

```bash
pip install web3
```

## Configuration

| Setting | File | Value |
|---------|------|-------|
| Contract Address | `frontend/app.js` | `CONTRACT_ADDRESS` |
| Contract Address | `crypto/export_ballots.py` | `CONTRACT_ADDRESS` |
| RPC URL | `crypto/export_ballots.py` | `RPC_URL` |
| Public Key | `frontend/public_key.json` | Auto-loaded |

## Network

Deployed and tested on **Ethereum Sepolia Testnet** (Chain ID: 11155111).

Get test ETH from: https://www.alchemy.com/faucets/ethereum-sepolia
