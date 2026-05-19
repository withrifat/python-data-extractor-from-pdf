import fitz
import re
import json
import os
from datetime import datetime
from tqdm import tqdm

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def extract_from_pdf(pdf_path):
    data = []
    institute = "Unknown Institute"
    total_matches = 0
    
    try:
        doc = fitz.open(pdf_path)
        filename = os.path.basename(pdf_path).lower()
        
        for page_num in range(len(doc)):
            text = doc[page_num].get_text("text")
            if not text:
                continue
            
            text_clean = clean_text(text)
            
            # Institute Name
            inst_match = re.search(r'(\d{4,6})\s*-\s*([^\n,]+)', text)
            if inst_match:
                institute = inst_match.group(0).strip()
            
            # === Multiple Regex Patterns (বিভিন্ন ফরম্যাটের জন্য) ===
            patterns = [
                r'(\d{5,})\s+cgpa:\s*([\d.]+)\s*\(([^)]*?)\)',           # Original
                r'(\d{5,})\s+CGPA:\s*([\d.]+)',                          # CGPA without gpa list
                r'Roll[:\s]*(\d{5,})\s.*?CGPA[:\s]*([\d.]+)',           # Roll + CGPA
                r'(\d{6,})\s+([23]\.\d{2})',                             # Roll + CGPA direct
            ]
            
            page_matches = 0
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    roll = match.group(1).strip()
                    try:
                        cgpa = float(match.group(2))
                        
                        # GPA list খোঁজার চেষ্টা
                        gpa_str = match.group(3) if len(match.groups()) > 2 else ""
                        semester_gpas = {}
                        for g in re.finditer(r'gpa(\d+):\s*([\d.]+)', gpa_str):
                            semester_gpas[f"gpa{g.group(1)}"] = float(g.group(2))
                        
                        student = {
                            "roll": roll,
                            "institute": institute,
                            "cgpa": cgpa,
                            "semester_gpas": semester_gpas,
                            "file_name": os.path.basename(pdf_path),
                            "page": page_num + 1,
                            "extracted_at": datetime.now().isoformat()
                        }
                        data.append(student)
                        page_matches += 1
                        total_matches += 1
                    except:
                        continue
                
                if page_matches > 0:
                    break  # একটা প্যাটার্ন কাজ করলে পরেরগুলো চেক করবে না
        
        doc.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return data


if __name__ == "__main__":
    pdf_folder = "Result"
    all_students = []
    
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    pdf_files.sort()
    
    print(f"🔍 মোট {len(pdf_files)} টি PDF প্রসেস করা হচ্ছে...\n")
    
    for pdf_file in tqdm(pdf_files, desc="Fast Extracting"):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"\n▶️  প্রসেস হচ্ছে: {pdf_file}")
        
        students = extract_from_pdf(pdf_path)
        all_students.extend(students)
        
        print(f"   ✅ {len(students)} জন ছাত্র এক্সট্র্যাক্ট হয়েছে")
    
    os.makedirs("output", exist_ok=True)
    
    output_file = "output/all_students_extracted.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_students, f, indent=2, ensure_ascii=False)
    
    with open("output/all_students_min.json", "w", encoding="utf-8") as f:
        json.dump(all_students, f, ensure_ascii=False, separators=(',', ':'))
    
    print("\n" + "="*70)
    print("🎉 এক্সট্র্যাকশন সম্পূর্ণ!")
    print(f"মোট ছাত্র : {len(all_students)} জন")
    print(f"সেভ হয়েছে ➜ {output_file}")
    print("="*70)