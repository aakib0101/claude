"""
Minimal PDF generator for Aakib's resume - no external dependencies.
Generates a clean, single-page resume in YashVeer's format.
"""
import struct
import zlib

class SimplePDF:
    def __init__(self):
        self.objects = []
        self.pages = []
        self.current_page_content = []
        self.fonts = {}
        self.y = 750  # Start near top of page (letter size: 612x792)
        self.left_margin = 45
        self.right_margin = 567
        self.page_width = 612
        
    def _add_object(self, content):
        self.objects.append(content)
        return len(self.objects)
    
    def _escape_text(self, text):
        return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
    
    def set_font(self, name, size):
        self.current_font = name
        self.current_size = size
        self.current_page_content.append(f"/{name} {size} Tf")
    
    def move_to(self, x, y):
        self.y = y
        self.current_page_content.append(f"1 0 0 1 {x} {y} Tm")
    
    def text_at(self, x, y, text):
        self.y = y
        escaped = self._escape_text(text)
        self.current_page_content.append(f"BT")
        self.current_page_content.append(f"/{self.current_font} {self.current_size} Tf")
        self.current_page_content.append(f"{x} {y} Td")
        self.current_page_content.append(f"({escaped}) Tj")
        self.current_page_content.append(f"ET")
    
    def draw_line(self, x1, y1, x2, y2, width=0.5):
        self.current_page_content.append(f"{width} w")
        self.current_page_content.append(f"{x1} {y1} m")
        self.current_page_content.append(f"{x2} {y2} l")
        self.current_page_content.append(f"S")
    
    def add_name(self, name):
        """Center the name at the top"""
        self.set_font("F1", 16)
        # Approximate centering
        text_width = len(name) * 8
        x = (self.page_width - text_width) / 2
        self.text_at(x, self.y, name)
        self.y -= 18
    
    def add_contact_line(self, text):
        """Center contact info"""
        self.set_font("F2", 9)
        text_width = len(text) * 4.2
        x = (self.page_width - text_width) / 2
        self.text_at(x, self.y, text)
        self.y -= 13
    
    def add_section_header(self, title):
        """Bold section header with underline"""
        self.y -= 6
        self.set_font("F1", 11)
        self.text_at(self.left_margin, self.y, title)
        self.y -= 3
        self.draw_line(self.left_margin, self.y, self.right_margin, self.y, 0.7)
        self.y -= 12
    
    def add_entry_header(self, left_bold, right_italic):
        """Entry with bold left text and italic right-aligned date"""
        self.set_font("F1", 9.5)
        self.text_at(self.left_margin, self.y, left_bold)
        self.set_font("F3", 9)
        text_width = len(right_italic) * 4.5
        x = self.right_margin - text_width
        self.text_at(x, self.y, right_italic)
        self.y -= 12
    
    def add_entry_subheader(self, left_italic, right_text=""):
        """Italic sub-entry"""
        self.set_font("F3", 9)
        self.text_at(self.left_margin + 2, self.y, left_italic)
        if right_text:
            text_width = len(right_text) * 4.3
            x = self.right_margin - text_width
            self.text_at(x, self.y, right_text)
        self.y -= 11
    
    def add_bullet(self, text):
        """Bullet point"""
        self.set_font("F2", 9)
        bullet_x = self.left_margin + 8
        self.text_at(bullet_x, self.y, "\x95  " + text)
        self.y -= 11
    
    def add_bullet_plain(self, text):
        """Bullet point without special char"""
        self.set_font("F2", 9)
        bullet_x = self.left_margin + 8
        # Use a simple dash or dot as bullet
        self.text_at(bullet_x, self.y, text)
        self.y -= 11

    def add_text(self, text, size=9, bold=False):
        """Regular text"""
        font = "F1" if bold else "F2"
        self.set_font(font, size)
        self.text_at(self.left_margin, self.y, text)
        self.y -= 11
    
    def generate(self):
        """Generate the final PDF bytes"""
        # Build the content stream
        content_str = "\n".join(self.current_page_content)
        content_bytes = content_str.encode('latin-1', errors='replace')
        
        # PDF structure
        pdf_parts = []
        pdf_parts.append(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        
        offsets = []
        
        def add_obj(obj_bytes):
            offsets.append(len(b"".join(pdf_parts)))
            pdf_parts.append(obj_bytes)
        
        # Object 1: Catalog
        add_obj(b"1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n")
        
        # Object 2: Pages
        add_obj(b"2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n")
        
        # Object 3: Page
        add_obj(b"3 0 obj\n<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
                b"/Contents 4 0 R/Resources<</Font<</F1 5 0 R/F2 6 0 R/F3 7 0 R>>>>>>\nendobj\n")
        
        # Object 4: Content stream
        compressed = zlib.compress(content_bytes)
        stream_obj = (f"4 0 obj\n<</Length {len(compressed)}/Filter/FlateDecode>>\n"
                     f"stream\n").encode('latin-1')
        stream_obj += compressed
        stream_obj += b"\nendstream\nendobj\n"
        add_obj(stream_obj)
        
        # Object 5: Font F1 (Helvetica-Bold)
        add_obj(b"5 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica-Bold/Encoding/WinAnsiEncoding>>\nendobj\n")
        
        # Object 6: Font F2 (Helvetica)
        add_obj(b"6 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica/Encoding/WinAnsiEncoding>>\nendobj\n")
        
        # Object 7: Font F3 (Helvetica-Oblique / Italic)
        add_obj(b"7 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica-Oblique/Encoding/WinAnsiEncoding>>\nendobj\n")
        
        # Cross-reference table
        xref_offset = len(b"".join(pdf_parts))
        xref = f"xref\n0 {len(offsets)+1}\n0000000000 65535 f \n"
        for off in offsets:
            xref += f"{off:010d} 00000 n \n"
        
        pdf_parts.append(xref.encode('latin-1'))
        
        # Trailer
        trailer = (f"trailer\n<</Size {len(offsets)+1}/Root 1 0 R>>\n"
                  f"startxref\n{xref_offset}\n%%EOF\n")
        pdf_parts.append(trailer.encode('latin-1'))
        
        return b"".join(pdf_parts)


def create_aakib_resume():
    pdf = SimplePDF()
    
    # === HEADER ===
    pdf.y = 760
    pdf.add_name("Mohd Aakib")
    
    # Contact info - matching YashVeer's format (location, email, phone, linkedin, github)
    pdf.add_contact_line("Chandigarh University, Mohali, Punjab - 140413")
    pdf.add_contact_line("22bcs10045@cuchd.in  |  +91-8319049218  |  linkedin.com/in/mohd-aakib  |  github.com/aakib0101")
    
    pdf.y -= 4
    
    # === EDUCATION ===
    pdf.add_section_header("Education")
    
    pdf.add_entry_header("B.E. in Computer Science Engineering", "Aug 2022 - Jun 2026")
    pdf.add_entry_subheader("Chandigarh University, Mohali", "CGPA: 7.2")
    
    pdf.add_entry_header("Senior Secondary (CBSE)", "Apr 2021 - Mar 2022")
    pdf.add_entry_subheader("M.G.M. Sr. Sec. School, Bhilai (C.G.)", "Percentage: 73%")
    
    pdf.add_entry_header("Matriculation (CBSE)", "Apr 2019 - Mar 2020")
    pdf.add_entry_subheader("M.G.M. Sr. Sec. School, Bhilai (C.G.)", "Percentage: 86%")
    
    # === EXPERIENCE ===
    pdf.add_section_header("Experience")
    
    pdf.add_entry_header("Wipro TalentNext - Digital Skills Readiness Program", "Jul 2025 - Oct 2025")
    pdf.set_font("F2", 9)
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Completed industry-oriented training in C# programming and .NET framework")
    pdf.y -= 11
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Gained strong understanding of Object-Oriented Programming (OOP) concepts using C#")
    pdf.y -= 11
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Developed applications using .NET technologies, applying real-world programming practices")
    pdf.y -= 12
    
    pdf.add_entry_header("In-House Training - C# and Data Structures", "Jun 2024 - Jul 2024")
    pdf.set_font("F2", 9)
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Solved coding problems enhancing algorithmic problem-solving speed by 40%")
    pdf.y -= 11
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Implemented optimized sorting and search algorithms, reducing execution time by 30%")
    pdf.y -= 12
    
    pdf.add_entry_header("Infosys Springboard - Cloud Computing", "May 2024 - Jul 2024")
    pdf.set_font("F2", 9)
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Completed certification in cloud computing fundamentals and deployment strategies")
    pdf.y -= 11
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Gained hands-on experience with cloud services and infrastructure management")
    pdf.y -= 12
    
    # === PROJECTS ===
    pdf.add_section_header("Projects")
    
    pdf.add_entry_header("E-Commerce Full Stack Web Application  -  React.js, Node.js, MongoDB, JWT", "Jan 2025")
    pdf.set_font("F2", 9)
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Built production-grade e-commerce platform with product catalog, cart, and Razorpay payment integration")
    pdf.y -= 11
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Implemented JWT-based authentication, protected routes, and role-based access control (Admin/Customer)")
    pdf.y -= 11
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Designed RESTful APIs in Node.js/Express connected to MongoDB Atlas with Mongoose ODM")
    pdf.y -= 12
    
    pdf.add_entry_header("Hospital Management System  -  PHP, MySQL, Bootstrap", "Oct 2023")
    pdf.set_font("F2", 9)
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Developed multi-role web system (Admin, Doctor, Patient) to manage hospital operations end-to-end")
    pdf.y -= 11
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Designed normalized relational database schema in MySQL with stored procedures for report generation")
    pdf.y -= 12
    
    pdf.add_entry_header("Real-Time Chat Application  -  React.js, Node.js, Socket.io, MongoDB", "Jul 2024")
    pdf.set_font("F2", 9)
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Built real-time messaging app supporting private and group chats with live status indicators")
    pdf.y -= 11
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Integrated Socket.io for WebSocket-based bidirectional communication with message history in MongoDB")
    pdf.y -= 12
    
    # === CERTIFICATIONS ===
    pdf.add_section_header("Certifications")
    pdf.set_font("F2", 9)
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Wipro TalentNext | Digital Skills Readiness Program (.NET & C#) - Jul 2025")
    pdf.y -= 11
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Infosys Springboard | Cloud Computing Certificate - May 2024")
    pdf.y -= 11
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Computer Architecture Organisation by NPTEL (Dec 2023)")
    pdf.y -= 11
    pdf.text_at(pdf.left_margin + 8, pdf.y, "- Team Skill, Psychology Certification, Coursera (Oct 2023)")
    pdf.y -= 12
    
    # === TECHNICAL SKILLS ===
    pdf.add_section_header("Technical Skills")
    pdf.set_font("F1", 9)
    pdf.text_at(pdf.left_margin, pdf.y, "Languages:")
    pdf.set_font("F2", 9)
    pdf.text_at(pdf.left_margin + 62, pdf.y, "C++, Java, Python, JavaScript, SQL, HTML5, CSS3, C#")
    pdf.y -= 12
    
    pdf.set_font("F1", 9)
    pdf.text_at(pdf.left_margin, pdf.y, "Web Development:")
    pdf.set_font("F2", 9)
    pdf.text_at(pdf.left_margin + 95, pdf.y, "React.js, Node.js, Express.js, PHP, REST APIs, TailwindCSS, Bootstrap")
    pdf.y -= 12
    
    pdf.set_font("F1", 9)
    pdf.text_at(pdf.left_margin, pdf.y, "Databases:")
    pdf.set_font("F2", 9)
    pdf.text_at(pdf.left_margin + 62, pdf.y, "MySQL, MongoDB")
    pdf.y -= 12
    
    pdf.set_font("F1", 9)
    pdf.text_at(pdf.left_margin, pdf.y, "Tools & Platforms:")
    pdf.set_font("F2", 9)
    pdf.text_at(pdf.left_margin + 100, pdf.y, "Git, GitHub, Postman, VS Code, Figma, Linux Terminal")
    pdf.y -= 12
    
    # Generate PDF
    return pdf.generate()


if __name__ == "__main__":
    pdf_bytes = create_aakib_resume()
    output_path = "/projects/sandbox/claude/Mohd_Aakib_Resume.pdf"
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"Resume generated: {output_path}")
    print(f"File size: {len(pdf_bytes)} bytes")
