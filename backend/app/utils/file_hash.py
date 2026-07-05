import hashlib


def generate_file_hash(file_bytes: bytes) -> str:
    """
    Generate a SHA256 hash for a file.
    """

    return hashlib.sha256(file_bytes).hexdigest()