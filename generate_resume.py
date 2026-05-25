"""
Generates Aakib's resume PDF in YashVeer's clean format.
No external dependencies - pure Python PDF generation.
"""
import zlib


class PDF:
    def __init__(self):
        self.content = []
        self.y = 760
        self.page_w = 612
        self.page_h = 792
        self.margin_l = 50
        self.margin_r = 562

    def _esc(self, t):
        return t.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

    def text(self, x, y, txt, font="F2", size=10):
        self.content.append(f"BT /{font} {size} Tf {x:.1f} {y:.1f} Td ({self._esc(txt)}) Tj ET")

    def line(self, x1, y1, x2, y2, w=0.5):
        self.content.append(f"{w} w {x1:.1f} {y1:.1f} m {x2:.1f} {y2:.1f} l S")

    def center_text(self, y, txt, font="F2", size=10):
        # Approximate width: size * 0.5 per char for Helvetica
        w = len(txt) * size * 0.52
        x = (self.page_w - w) / 2
        self.text(x, y, txt, font, size)

    def right_text(self, y, txt, font="F2", size=9):
        w = len(txt) * size * 0.5
        x = self.margin_r - w
        self.text(x, y, txt, font, size)

    def section(self, title):
        """Section header with line underneath"""
        self.y -= 14
        self.text(self.margin_l, self.y, title, "F1", 11)
        self.y -= 4
        self.line(self.margin_l, self.y, self.margin_r, self.y, 0.6)
        self.y -= 14

    def entry(self, left, right="", left_font="F1", left_size=9.5):
        """Bold left + italic right aligned date"""
        self.text(self.margin_l, self.y, left, left_font, left_size)
        if right:
            self.right_text(self.y, right, "F3", 9)
        self.y -= 13

    def subentry(self, left, right=""):
        """Italic subline"""
        self.text(self.margin_l + 4, self.y, left, "F3", 9)
        if right:
            self.right_text(self.y, right, "F3", 9)
        self.y -= 13

    def bullet(self, txt):
        """Bullet point with proper indent"""
        self.text(self.margin_l + 10, self.y, "- " + txt, "F2", 9)
        self.y -= 12

    def skill_line(self, label, value):
        """Bold label: regular value"""
        self.text(self.margin_l, self.y, label, "F1", 9)
        label_w = len(label) * 9 * 0.55
        self.text(self.margin_l + label_w + 4, self.y, value, "F2", 9)
        self.y -= 13

    def build(self):
        stream = "\n".join(self.content).encode("latin-1", errors="replace")
        compressed = zlib.compress(stream)
        sl = len(compressed)

        objs = []
        objs.append(b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n")
        objs.append(b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n")
        objs.append(b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
                    b"/Contents 4 0 R/Resources<</Font<</F1 5 0 R/F2 6 0 R/F3 7 0 R>>>>>>endobj\n")
        objs.append(f"4 0 obj<</Length {sl}/Filter/FlateDecode>>stream\n".encode() + compressed + b"\nendstream\nendobj\n")
        objs.append(b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica-Bold/Encoding/WinAnsiEncoding>>endobj\n")
        objs.append(b"6 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica/Encoding/WinAnsiEncoding>>endobj\n")
        objs.append(b"7 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica-Oblique/Encoding/WinAnsiEncoding>>endobj\n")

        out = b"%PDF-1.4\n"
        offsets = []
        for o in objs:
            offsets.append(len(out))
            out += o

        xref_pos = len(out)
        out += f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode()
        for off in offsets:
            out += f"{off:010d} 00000 n \n".encode()
        out += f"trailer<</Size {len(objs)+1}/Root 1 0 R>>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
        return out


def main():
    p = PDF()

    # ===== HEADER =====
    p.y = 756
    p.center_text(p.y, "Mohd Aakib", "F1", 18)
    p.y -= 18

    p.center_text(p.y, "Chandigarh University, Mohali, Punjab  140413", "F2", 9)
    p.y -= 13

    p.center_text(p.y, "22bcs10045@cuchd.in   +91-8319049218   linkedin.com/in/mohd-aakib   github.com/aakib0101", "F2", 8.5)
    p.y -= 6

    # ===== EDUCATION =====
    p.section("Education")

    p.entry("B.E. in Computer Science Engineering", "Aug 2022 - Jun 2026")
    p.subentry("Chandigarh University, Mohali", "CGPA: 7.2")

    p.entry("Senior Secondary (CBSE)", "Apr 2021 - Mar 2022")
    p.subentry("M.G.M. Sr. Sec. School, Bhilai (C.G.)", "Percentage: 73%")

    p.entry("Matriculation (CBSE)", "Apr 2019 - Mar 2020")
    p.subentry("M.G.M. Sr. Sec. School, Bhilai (C.G.)", "Percentage: 86%")

    # ===== EXPERIENCE =====
    p.section("Experience")

    p.entry("Wipro TalentNext  |  Digital Skills Readiness Program (.NET/C#)", "Jul 2025 - Oct 2025")
    p.bullet("Completed industry-oriented training in C# programming and .NET framework")
    p.bullet("Gained understanding of OOP concepts using C# and developed real-world applications")
    p.bullet("Worked on hands-on assignments and coding exercises to improve problem-solving skills")
    p.y -= 2

    p.entry("In-House Training  |  C# and Data Structures & Algorithms", "Jun 2024 - Jul 2024")
    p.bullet("Solved coding problems, enhancing algorithmic problem-solving speed by 40%")
    p.bullet("Implemented optimized sorting and search algorithms, reducing execution time by 30%")
    p.y -= 2

    p.entry("Infosys Springboard  |  Cloud Computing Certificate", "May 2024 - Jul 2024")
    p.bullet("Completed certification in cloud computing fundamentals and deployment strategies")
    p.bullet("Gained hands-on experience with cloud services and infrastructure management")

    # ===== PROJECTS =====
    p.section("Projects")

    p.entry("E-Commerce Platform    React.js, Node.js, Express, MongoDB", "Jan 2025")
    p.bullet("Built production-grade e-commerce with product catalog, cart, order management, Razorpay")
    p.bullet("Implemented JWT authentication, protected routes, role-based access (Admin/Customer)")
    p.bullet("Designed RESTful APIs connected to MongoDB Atlas; deployed on Vercel and Render")
    p.y -= 2

    p.entry("Hospital Management System    PHP, MySQL, JavaScript, Bootstrap", "Oct 2023")
    p.bullet("Developed multi-role system (Admin, Doctor, Patient) managing end-to-end operations")
    p.bullet("Designed normalized database schema with stored procedures for report generation")
    p.y -= 2

    p.entry("Real-Time Chat Application    React.js, Node.js, Socket.io, MongoDB", "Jul 2024")
    p.bullet("Built real-time messaging supporting private/group chats with live status indicators")
    p.bullet("Integrated Socket.io for bidirectional communication; message history stored in MongoDB")

    # ===== CERTIFICATIONS =====
    p.section("Certifications")
    p.bullet("Wipro/TalentNext | Digital Skills Readiness Program (.NET & C#) | July - October 2025")
    p.bullet("Infosys Springboard | Cloud Computing Certificate | May 2024")
    p.bullet("Computer Architecture Organisation by NPTEL (Dec 2023)")
    p.bullet("Team Skill, Psychology Certification, Coursera (Oct 2023)")

    # ===== TECHNICAL SKILLS =====
    p.section("Technical Skills")
    p.skill_line("Languages:", "C++, Java, Python, JavaScript, C#, SQL, HTML5, CSS3")
    p.skill_line("Web Development:", "React.js, Node.js, Express.js, PHP, REST APIs, TailwindCSS, Bootstrap")
    p.skill_line("Databases:", "MySQL, MongoDB")
    p.skill_line("Tools & Platforms:", "Git, GitHub, Postman, VS Code, Figma, Linux Terminal")
    p.skill_line("Other Skills:", "Data Structures, Algorithms, Responsive Design, Agile/Scrum")

    # Generate
    pdf_bytes = p.build()
    out_path = "/projects/sandbox/claude/Mohd_Aakib_Resume.pdf"
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"Generated: {out_path} ({len(pdf_bytes)} bytes)")
    print(f"Final Y position: {p.y:.0f} (page bottom ~30, so {'FITS' if p.y > 30 else 'OVERFLOW'})")


if __name__ == "__main__":
    main()
