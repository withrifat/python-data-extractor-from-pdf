import pdfplumber
import re
import json
import os
from datetime import datetime
from tqdm import tqdm

def extract_from_pdf(pdf_path):
    data = []
    institute = "Unknown Institute"
    filename = os.path.basename(pdf_path)
    total = 0
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for i in range(len(pdf.pages)):
                page = pdf.pages[i]
                text = page.extract_text(x_tolerance=1, y_tolerance=1)
                if text:
                    full_text += text + "\n"
            
            # Institute Name
            inst_match = re.search(r'(\d{4,6})\s*-\s*([^\n,]+)', full_text)
            if inst_match:
                institute = inst_match.group(0).strip()

            # ==================== PATTERNS ====================
            patterns = [
                r'(\d{5,})\s+cgpa:\s*([\d.]+)\s*\(([^)]*?)\)',     # Normal
                r'(\d{5,})\s*\{([^}]*)\}',                        # Referred with {}
                r'(\d{5,})\s*\(([^)]*?Expelled|reffered|referred|ref_sub[^)]*?)\)'  # Expelled line
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, full_text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    try:
                        roll = match.group(1).strip()
                        content = match.group(2) if len(match.groups()) > 1 else ""
                        
                        # CGPA
                        cgpa_match = re.search(r'cgpa:\s*([\d.]+)', content, re.IGNORECASE)
                        cgpa = float(cgpa_match.group(1)) if cgpa_match else None
                        
                        # Semester GPAs (including 'ref')
                        semester_gpas = {}
                        for g in re.finditer(r'gpa(\d+):\s*([\d.]+|ref)', content, re.IGNORECASE):
                            sem = f"gpa{g.group(1)}"
                            val = g.group(2).strip()
                            semester_gpas[sem] = val if val.lower() == "ref" else float(val)
                        
                        # Referred Subjects - Refined Regex
                        ref_sub = []
                        ref_matches = re.findall(r'ref_sub[:\s-]*([^\n,}]+)', content, re.IGNORECASE)
                        for rm in ref_matches:
                            codes = re.findall(r'(\d{5,}[(TP)]?)', rm)
                            ref_sub.extend(codes)
                        
                        # Extra Note
                        extra_note = ""
                        if any(word in content.lower() for word in ["expelled", "reffered", "referred"]):
                            extra_note = content.strip()[:500]
                        
                        student = {
                            "roll": roll,
                            "institute": institute,
                            "cgpa": cgpa,
                            "semester_gpas": semester_gpas,
                            "referred_subjects": ref_sub,
                            "status": "Referred" if (ref_sub or any(v == "ref" for v in semester_gpas.values())) else "Passed",
                            "extra_note": extra_note,
                            "file_name": filename,
                            "extracted_at": datetime.now().isoformat()
                        }
                        data.append(student)
                        total += 1
                    except:
                        continue
                        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"   ✅ {total} জন ছাত্র এক্সট্র্যাক্ট হয়েছে")
    return data


if __name__ == "__main__":
    pdf_folder = "Result"
    all_students = []
    
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    pdf_files.sort()
    
    print(f"🔍 মোট {len(pdf_files)} টি PDF প্রসেস করা হচ্ছে...\n")
    
    for pdf_file in tqdm(pdf_files, desc="Reliable Extraction"):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"\n▶️  {pdf_file}")
        students = extract_from_pdf(pdf_path)
        all_students.extend(students)
    
    os.makedirs("output", exist_ok=True)
    
    output_file = "output/all_students_reliable_full.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_students, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*80)
    print("🎉 সম্পূর্ণ হয়েছে!")
    print(f"মোট ছাত্র : {len(all_students)} জন")
    print(f"সেভ হয়েছে ➜ {output_file}")
    print("="*80)