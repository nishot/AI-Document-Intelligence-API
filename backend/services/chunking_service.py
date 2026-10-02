from transformers import AutoTokenizer

tokenizer=AutoTokenizer.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2"
)

from pdf_service import extract_text_from_pdf
text_data=extract_text_from_pdf("D:/chapter_15_literature/Paper_2.pdf")


def count_tokens(item):
    tokens=tokenizer.encode(
        item,
        add_special_tokens=False
        )
    return len(tokens)

def split_into_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

# def split_into_paragraph(text)->list[str]:
#     paragraphs=text.split('\n\n')
#     return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]

def inspect_doc(text_data):
    for page in text_data:
        lines=split_into_lines(page['text'])
        for i , paragraph in enumerate(lines):
            print("==========================")
            tokens=count_tokens(paragraph)
            # print("line",i+1)
            print("tokens",tokens)
            print(i,repr(lines))


# def chunking(text_data):
#     chunk_size=600
#     max=1000
#     overlap=100
#     curr_chunk=[]
#     curr_token=0
#     separators = [
#     "\n\n",   # paragraph
#     "\n",     # line
#     ". ",     # sentence-ish
#     " ",      # word
#     ]
#     for item in text_data:
#         count=count_tokens(item['text'])
#         splitted=split_into_paragraph(item['text'])
#         print(count)
#         print(splitted)


# chunking(text_data)
inspect_doc(text_data)