import pdfplumber
import re
import json
from tqdm import tqdm
import os
from datetime import datetime

def extract_from_pdf(pdf_path):
    data = []
    institute = "Unknown"
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf:
                text = page.extract_text()
                if not text:
                    continue
                
                # Institute Name খোঁজা
                inst_match = re.search(r'(\d{4,6})\s*-\s*([^\n,]+)', text)
                if inst_match:
                    institute = inst_match.group(0).strip()
                
                # Student Results Extract
                matches = re.finditer(
                    r'(\d{6,})\s+cgpa:\s*([\d.]+)\s*\((.*?)\)', 
                    text, re.IGNORECASE | re.DOTALL
                )
                
                for match in matches:
                    roll = match.group(1).strip()
                    cgpa = float(match.group(2))
                    gpa_str = match.group(3)
                    
                    semester_gpas = {}
                    for g in re.finditer(r'gpa(\d+):\s*([\d.]+)', gpa_str):
                        semester_gpas[f"gpa{g.group(1)}"] = float(g.group(2))
                    
                    student = {
                        "roll": roll,
                        "institute": institute,
                        "cgpa": cgpa,
                        "semester_gpas": semester_gpas,
                        "file_name": os.path.basename(pdf_path),
                        "extracted_at": datetime.now().isoformat()
                    }
                    data.append(student)
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
    
    return data


if __name__ == "__main__":
    pdf_folder = "Result"
    all_students = []
    
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    
    print(f"মোট {len(pdf_files)} টি PDF ফাইল পাওয়া গেছে\n")
    
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"→ প্রসেস হচ্ছে: {pdf_file}")
        
        students = extract_from_pdf(pdf_path)
        all_students.extend(students)
        print(f"   ✅ {len(students)} জন ছাত্র এক্সট্র্যাক্ট হয়েছে\n")
    
    # Output ফোল্ডার তৈরি
    os.makedirs("output", exist_ok=True)
    
    with open("output/all_students.json", "w", encoding="utf-8") as f:
        json.dump(all_students, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 সম্পূর্ণ হয়েছে!")
    print(f"মোট ছাত্র: {len(all_students)} জন")
    print(f"ফাইল সেভ হয়েছে: output/all_students.json")