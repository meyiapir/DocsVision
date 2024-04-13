import hashlib


def text_to_hash(text):
    text = text.encode('utf-8')

    # Create a hash object using SHA-256 algorithm
    hash_object = hashlib.sha256()

    # Update the hash object with the encoded text
    hash_object.update(text)

    # Get the hexadecimal representation of the hash
    hashed_text = hash_object.hexdigest()

    return hashed_text
