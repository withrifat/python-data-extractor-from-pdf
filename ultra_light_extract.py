import fitz
import re
import json
import os
import gc
from datetime import datetime
from tqdm import tqdm

def extract_from_pdf(pdf_path):
    data = []
    institute = "Unknown Institute"
    filename = os.path.basename(pdf_path)
    total = 0
    
    try:
        doc = fitz.open(pdf_path)
        print(f"   📄 পেজ: {len(doc)}")
        
        for page_num in range(len(doc)):
            text = doc[page_num].get_text("text")
            if not text:
                continue
            
            if page_num == 0:
                inst_match = re.search(r'(\d{4,6})\s*-\s*([^\n,]+)', text)
                if inst_match:
                    institute = inst_match.group(0).strip()

            # Patterns
            patterns = [
                r'(\d{5,})\s*\(\s*([\d.]+)\s*\)',     
                r'(\d{5,})\s*\{([^}]+)\}',             
                r'(\d{5,})\s+cgpa:\s*([\d.]+)',        
            ]
            
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    try:
                        roll = match.group(1).strip()
                        content = match.group(2).strip() if len(match.groups()) > 1 else ""
                        
                        cgpa_match = re.search(r'([\d.]{3,})', content)
                        cgpa = float(cgpa_match.group(1)) if cgpa_match else None
                        
                        ref_sub = re.findall(r'(\d{5,}[(TP)]?)', content)
                        
                        student = {
                            "roll": roll,
                            "institute": institute,
                            "cgpa": cgpa,
                            "referred_subjects": ref_sub,
                            "status": "Referred" if ref_sub else "Passed",
                            "extra_note": content[:300] if ref_sub else "",
                            "file_name": filename,
                            "page": page_num + 1,
                            "extracted_at": datetime.now().isoformat()
                        }
                        data.append(student)
                        total += 1
                    except:
                        continue
            
            if page_num % 5 == 0:
                gc.collect()
        
        doc.close()
        gc.collect()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"   ✅ {total} জন ছাত্র এক্সট্র্যাক্ট হয়েছে")
    return data


if __name__ == "__main__":
    pdf_folder = "Result"
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)
    
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    pdf_files.sort()
    
    print("🚀 Ultra Light Mode চালু হয়েছে (মেমরি খুব কম লাগবে)\n")
    
    for i, pdf_file in enumerate(tqdm(pdf_files, desc="Processing"), 1):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"\n[{i:2d}/{len(pdf_files)}] → {pdf_file}")
        
        students = extract_from_pdf(pdf_path)
        
        json_path = os.path.join(output_folder, pdf_file.replace(".pdf", ".json"))
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(students, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 সেভ হয়েছে → {pdf_file.replace('.pdf','.json')} ({len(students)} records)")
        
        del students
        gc.collect()
    
    print("\n🎉 সব PDF প্রসেসিং সম্পূর্ণ হয়েছে!")