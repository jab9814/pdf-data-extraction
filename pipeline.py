from constants import INPUT_FILE, OUTPUT_FILE
from enums import INIDCode, Section
from utils import load_json, save_json, get_headers, split_columns, pair_inid_values


def main():
    data = load_json(INPUT_FILE)
    b1_pages = get_section_pages(data, Section.B1, Section.B2)
    records = build_records(b1_pages)

    output = {"B": {"1": records}}
    save_json(OUTPUT_FILE, output)

    print(f"Total registros: {len(records)}")
    print(f"Archivo generado: {OUTPUT_FILE}")



def get_section_pages(data, section_start, section_end):
    """Return pages belonging to section B.1."""
    in_section = False
    pages = []

    for page in data:
        all_texts = [tb["text"].strip() for tb in page["textboxhorizontal"]]
        headers = get_headers(page)
        if any(section_start in text for text in all_texts):
            in_section = True
        if any(section_end in header for header in headers):
            break
        if in_section:
            pages.append(page)

    return pages


def build_records(pages):
    """Group INID pairs into records, handling cross-column and cross-page splits."""
    records = []
    current = None

    for page in pages:
        left, right = split_columns(page)
        columns = [left, right]

        for column in columns:
            pairs = pair_inid_values(column)

            for inid, value in pairs:
                if inid == INIDCode.REGISTRATION_NUMBER:
                    if current:
                        records.append(current)
                    current = {"_PAGE": page["page"], INIDCode.REGISTRATION_NUMBER.value: value}
                elif current is not None:
                    if inid == INIDCode.PRIOR_REGISTRATION:
                        current.setdefault(INIDCode.PRIOR_REGISTRATION.value, []).append(value)
                    else:
                        current[inid] = value

    if current:
        records.append(current)

    return records


if __name__ == "__main__":
    main()