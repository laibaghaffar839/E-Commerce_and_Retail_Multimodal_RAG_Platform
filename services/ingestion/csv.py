import pandas as pd


def extract_csv(file_path: str) -> list[str]:
    """
    Extract data from a CSV file.
    Each row is converted into a plain text string.
    """

    df = pd.read_csv(file_path)
    extracted_text = []

    for _, row in df.iterrows():
        row_text = " | ".join(
            f"{column}: {value}"
            for column, value in row.items()
        )

        extracted_text.append(row_text)

    return extracted_text