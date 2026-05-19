import pdfplumber
import re
import json
import os
import gc
from datetime import datetime
from tqdm import tqdm

def extract_from_single_pdf(pdf_path):
    """একটা PDF প্রসেস করে মেমরি ক্লিয়ার করে"""
    data = []
    institute = "Unknown Institute"
    filename = os.path.basename(pdf_path)
    total = 0
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"   📄 পেজ সংখ্যা: {len(pdf.pages)}")
            
            for page_num, page in enumerate(pdf.pages):
                # প্রতি পেজ আলাদা প্রসেস (মেমরি কম লাগে)
                text = page.extract_text(x_tolerance=1, y_tolerance=1)
                if not text:
                    continue
                
                # Institute Name (প্রথম পেজে খুঁজবে)
                if page_num == 0:
                    inst_match = re.search(r'(\d{4,6})\s*-\s*([^\n,]+)', text)
                    if inst_match:
                        institute = inst_match.group(0).strip()

                # Patterns
                patterns = [
                    r'(\d{5,})\s*\(\s*([\d.]+)\s*\)',           # Roll ( CGPA )
                    r'(\d{5,})\s*\{([^}]+)\}',                  # Roll { subjects }
                    r'(\d{5,})\s+cgpa:\s*([\d.]+)',             # Normal CGPA
                ]
                
                for pattern in patterns:
                    for match in re.finditer(pattern, text, re.IGNORECASE | re.DOTALL):
                        try:
                            roll = match.group(1).strip()
                            content = match.group(2).strip() if len(match.groups()) > 1 else ""
                            
                            # CGPA
                            cgpa = None
                            cgpa_match = re.search(r'([\d.]{3,})', content)
                            if cgpa_match:
                                cgpa = float(cgpa_match.group(1))
                            
                            # Referred Subjects
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
                        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # মেমরি ক্লিয়ার
    del text
    gc.collect()
    
    print(f"   ✅ {total} জন ছাত্র এক্সট্র্যাক্ট হয়েছে")
    return data


if __name__ == "__main__":
    pdf_folder = "Result"
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)
    
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    pdf_files.sort()
    
    print(f"🔍 মোট {len(pdf_files)} টি PDF প্রসেস হবে (মেমরি অপটিমাইজড মোড)\n")
    
    for i, pdf_file in enumerate(tqdm(pdf_files, desc="Memory Optimized Processing"), 1):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"\n[{i:2d}/{len(pdf_files)}] ▶️  {pdf_file}")
        
        # একটা PDF প্রসেস করা
        students = extract_from_single_pdf(pdf_path)
        
        # আলাদা JSON সেভ
        json_filename = pdf_file.replace(".pdf", ".json")
        json_path = os.path.join(output_folder, json_filename)
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(students, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 সেভ হয়েছে → {json_filename} ({len(students)} records)")
        
        # প্রত্যেক PDF এর পর মেমরি ক্লিয়ার
        del students
        gc.collect()
        print(f"   🧹 মেমরি ক্লিয়ার করা হয়েছে\n")
    
    print("\n🎉 সব PDF একটা একটা করে সম্পূর্ণ প্রসেস হয়েছে!")
    print(f"✅ সব ফাইল output ফোল্ডারে সেভ হয়েছে")