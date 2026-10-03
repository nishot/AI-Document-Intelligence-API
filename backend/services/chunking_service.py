from transformers import AutoTokenizer
# from pdf_service import extract_text_from_pdf


tokenizer=AutoTokenizer.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2"
)
target_tokens=400
max_token=450
overlap=50



# text_data=extract_text_from_pdf("D:/chapter_15_literature/Paper_2.pdf")


def count_tokens(item):
    tokens=tokenizer.encode(
        item,
        add_special_tokens=False
        )
    return len(tokens)


def split_text(text:str,max_tokens:int=450):
    words=text.split()
    current=[]
    chunks=[]
    for word in words:
        test=" ".join(current+[word])
        if count_tokens(test) <=max_tokens:
            current.append(word)
        else:
            if current:
                chunks.append(" ".join(current))
            current=[word]
    if current:
        chunks.append(" ".join(current))

    return chunks

def create_chunk(text_data):
    chunks=[]
    for page in text_data:
        page_no=page["page_no"]
        text=page['text'].strip()

        blocks=[
            block.strip()
            for block in text.split("\n\n")
            if block.strip()
        ]
        for block in blocks:
            small_chunks=split_text(block,max_tokens=450)
            for small_chunk in small_chunks:
                chunks.append({
                    "page_no":page_no,
                    "text":small_chunk,
                    "token_count":count_tokens(small_chunk)
                })
    return chunks



# if __name__=="__main__":
#     print(create_chunk(text_data))
