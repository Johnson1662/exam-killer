"""MinerU SDK thin wrapper."""

from mineru import MinerU


def parse_pdf(token: str, file_path: str, pages: str = "1-30"):
    """Run precision extraction via MinerU SDK.

    Returns ``ExtractResult`` with ``.markdown``, ``.content_list``,
    ``.images`` (dict of hash → bytes), and ``.save_markdown(path, with_images)``.
    """
    client = MinerU(token)
    result = client.extract(file_path, model="vlm", pages=pages)
    return result
