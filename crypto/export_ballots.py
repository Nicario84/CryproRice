import json
from web3 import Web3

# =========================
# CONFIG
# =========================

RPC_URL = "https://sepolia.infura.io/v3/4f55ca0ce3724047ba7fa5a5ba848467"
CONTRACT_ADDRESS = "0x2C7059d38452682f9E3F22a216DE1e257fA0Eed8"

# Minimal ABI needed for export
CONTRACT_ABI = [
    {
        "inputs": [],
        "name": "getVoterList",
        "outputs": [
            {
                "internalType": "address[]",
                "name": "",
                "type": "address[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "name": "encryptedBallot",
        "outputs": [
            {
                "internalType": "bytes",
                "name": "",
                "type": "bytes"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getCandidates",
        "outputs": [
            {
                "components": [
                    {
                        "internalType": "string",
                        "name": "name",
                        "type": "string"
                    },
                    {
                        "internalType": "uint256",
                        "name": "voteCount",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct PrivateVoting.Candidate[]",
                "name": "",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "votingEnd",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]


def main():
    print("Connecting to Sepolia...")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    if not w3.is_connected():
        print("Failed to connect to Sepolia.")
        return

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=CONTRACT_ABI
    )

    print("Reading candidates...")
    raw_candidates = contract.functions.getCandidates().call()
    candidate_names = [candidate[0] for candidate in raw_candidates]

    # Check if voting period is over
    import time
    voting_end = contract.functions.votingEnd().call()
    current_time = int(time.time())

    if current_time <= voting_end:
        remaining = voting_end - current_time
        print(f"\nVoting is still active! {remaining} seconds remaining.")
        print("You can only export ballots after voting has ended.")
        return

    print("Voting period is over. Proceeding with export...")
    print()

    print("Reading voter list...")
    voters = contract.functions.getVoterList().call()

    ballots = []

    print(f"Found {len(voters)} voters.")
    for voter in voters:
        encrypted_vote = contract.functions.encryptedBallot(voter).call()

        ballots.append({
            "voter": voter,
            "encryptedVote": encrypted_vote.hex()
        })

    result = {
        "candidates": candidate_names,
        "approvedVoters": [],
        "ballots": ballots
    }

    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    voters_path = os.path.join(script_dir, "..", "data", "voters.json")

    with open(voters_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    print()
    print("Export completed successfully.")
    print(f"Saved to {voters_path}")
    print(f"Candidates: {candidate_names}")
    print(f"Exported ballots: {len(ballots)}")


if __name__ == "__main__":
    main()
