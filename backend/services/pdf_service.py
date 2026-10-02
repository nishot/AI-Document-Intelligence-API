import pymupdf


def extract_text_from_pdf(userinputpdf):
    text_pages=[]
    with pymupdf.open(userinputpdf) as doc:
        for page in doc:
            page_number = page.number if page.number is not None else 0
            text_pages.append({
                "page_no": int(page_number) + 1,
                "text": page.get_text()
            })

    # print(text_pages)
    return text_pages
    # return "\n".join(text_pages)
    
    


if __name__=="__main__":
    ex_text=extract_text_from_pdf("backend/data/Sample Printable Document.pdf")

