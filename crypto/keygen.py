import json
import os
import secrets


# A small prime and generator for demo/testing.
# For a more serious system, these should be much larger.
P = 467
G = 2


def generate_keys():
	# Private key x must be in [1, p-2]
	x = secrets.randbelow(P - 2) + 1

	# Public key y = g^x mod p
	y = pow(G, x, P)

	public_key = {
		"p": P,
		"g": G,
		"y": y
	}

	private_key = {
		"p": P,
		"g": G,
		"x": x
	}

	return public_key, private_key


def save_json(path, data):
	with open(path, "w", encoding="utf-8") as f:
		json.dump(data, f, indent=4)


def main():
	script_dir = os.path.dirname(os.path.abspath(__file__))
	data_dir = os.path.join(script_dir, "..", "data")
	frontend_dir = os.path.join(script_dir, "..", "frontend")
	os.makedirs(data_dir, exist_ok=True)
	os.makedirs(frontend_dir, exist_ok=True)

	public_key, private_key = generate_keys()

	public_key_path = os.path.join(frontend_dir, "public_key.json")
	private_key_path = os.path.join(data_dir, "private_key.json")

	save_json(public_key_path, public_key)
	save_json(private_key_path, private_key)

	print("ElGamal keys generated successfully.")
	print(f"Public key saved to: {public_key_path}")
	print(f"Private key saved to: {private_key_path}")
	print()
	print("Public key:")
	print(json.dumps(public_key, indent=4))
	print()
	print("Private key:")
	print(json.dumps(private_key, indent=4))


if __name__ == "__main__":
	main()
