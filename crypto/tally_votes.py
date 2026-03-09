import json
from collections import Counter


def load_json(path):
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)


def mod_inverse(a, p):
	# Fermat's little theorem since p is prime
	return pow(a, p - 2, p)


def elgamal_decrypt(c1, c2, private_key):
	p = private_key["p"]
	x = private_key["x"]

	s = pow(c1, x, p)
	s_inv = mod_inverse(s, p)
	m = (c2 * s_inv) % p
	return m


def parse_ciphertext_string(text):
	# Expected format: "c1:c2"
	parts = text.strip().split(":")
	if len(parts) != 2:
		raise ValueError(f"Invalid ciphertext format: {text}")
	c1 = int(parts[0])
	c2 = int(parts[1])
	return c1, c2


def hex_to_text(hex_string):
	if hex_string.startswith("0x"):
		hex_string = hex_string[2:]
	raw = bytes.fromhex(hex_string)
	return raw.decode("utf-8")


def decrypt_vote_hex(hex_ciphertext, private_key):
	text = hex_to_text(hex_ciphertext)
	c1, c2 = parse_ciphertext_string(text)
	return elgamal_decrypt(c1, c2, private_key)


def build_result_array(counter, candidate_count):
	# candidate ids are 1..candidate_count
	result = []
	for candidate_id in range(1, candidate_count + 1):
		result.append(counter.get(candidate_id, 0))
	return result


def main():
	print("=== Private Voting Tally Program ===")
	print()

	private_key = load_json("../data/private_key.json")
	voters_data = load_json("../data/voters.json")

	candidate_names = voters_data.get("candidates", [])
	ballots = voters_data.get("ballots", [])

	if not candidate_names:
		print("No candidates found in ../data/voters.json")
		return

	if not ballots:
		print("No ballots found in ../data/voters.json")
		return

	candidate_count = len(candidate_names)
	counter = Counter()

	print("Decrypting ballots...")
	print()

	for ballot in ballots:
		voter = ballot["voter"]
		encrypted_vote = ballot["encryptedVote"]

		try:
			vote_value = decrypt_vote_hex("0x" + encrypted_vote, private_key)

			if 1 <= vote_value <= candidate_count:
				counter[vote_value] += 1
				print(f"Voter {voter} -> decrypted choice: {vote_value}")
			else:
				print(f"Voter {voter} -> invalid decrypted value: {vote_value}")

		except Exception as e:
			print(f"Failed to decrypt ballot for {voter}: {e}")

	final_counts = build_result_array(counter, candidate_count)

	result_data = {
		"candidates": candidate_names,
		"finalCounts": final_counts
	}

	with open("../data/tally_result.json", "w", encoding="utf-8") as f:
		json.dump(result_data, f, indent=4)

	print()
	print("=== Final Result ===")
	for i, name in enumerate(candidate_names, start=1):
		print(f"{i} = {name}: {final_counts[i - 1]} votes")

	print()
	print("Array to paste into the smart contract:")
	print(final_counts)
	print()
	print("Saved to ../data/tally_result.json")


if __name__ == "__main__":
	main()
