from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import tkinter as tk
from tkinter import ttk, messagebox
import time

def extract_courses(selected_department):
    url = "https://arch.cankaya.edu.tr/dersler-8/"
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    time.sleep(3)

    content_find = driver.find_element(By.CLASS_NAME, "page_content")

    elements = content_find.find_elements(By.XPATH, ".//*[(self::h2 or self::h4)]")

    # Seçmeli dersleri tutacak liste
    elective_courses = set()
    is_elective_section = False 

    for element in elements:
        if element.tag_name == "h2":  
            is_elective_section = "SEÇMELİ DERS" in element.text.upper()  
        elif element.tag_name == "h4" and is_elective_section:  
            elective_courses.add(element.text[:8])

    driver.quit()
    print(elective_courses)
    print("\t \t")
    return elective_courses


def get_courses_from_web(selected_course_type):
    url = "https://www.cankaya.edu.tr/dersler/"
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    time.sleep(2)
    if selected_course_type == "Bölüm İçi Teknik Seçmeliler":
        selected_course_type = "ARCH"
    courses = set()
    try:
        dropdown = driver.find_element(By.NAME, "DersCode")
        dropdown.send_keys(selected_course_type)
        dropdown.send_keys(Keys.RETURN)
        time.sleep(3)
        
        if selected_course_type != "HEPSİ":
            table_rows = driver.find_elements(By.XPATH, "//tr[@role='row']")
            for row in table_rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                
                if cols and selected_course_type in cols[0].text: #-----------------------------------------------!
                    
                    course_code = cols[0].text.replace("\u00a0", " ").strip().upper()  # Özel boşluk karakterlerini düzelt ve normalleştir
                    courses.add(course_code)
        driver.quit()
        print(courses)
        return courses

    except:
        driver.quit()
        return set()
    

def fetch_courses():
    selected_department = department_var.get()
    selected_course_type = course_type_var.get()
    
    if not selected_department:
        messagebox.showwarning("Uyarı", "Lütfen bir bölüm seçin!")
        return
    
    course_set = extract_courses(selected_department).intersection(get_courses_from_web(selected_course_type))
    sorted_courses = sorted(course_set)  # Alfabetik sıralama burada yapılıyor
    
    listbox.delete(0, tk.END)
    for course in sorted_courses:
        listbox.insert(tk.END, course)

# Ana pencere
root = tk.Tk()
root.title("Ders Seçim Arayüzü")
root.geometry("1000x600")

ttk.Label(root, text="Bölüm Seçiniz:").pack(pady=5)

department_var = tk.StringVar()
department_dropdown = ttk.Combobox(root, textvariable=department_var)
department_dropdown['values'] = ("ARCH")
department_dropdown.pack(pady=5)

ttk.Label(root, text="Ders Tipi Seçiniz:").pack(pady=5)
course_type_var = tk.StringVar()
course_type_dropdown = ttk.Combobox(root, textvariable=course_type_var)
course_type_dropdown['values'] = ("Bölüm İçi Teknik Seçmeliler", "Bölüm Dışı Teknik Seçmeliler", "Sosyal seçmeliler")
course_type_dropdown.pack(pady=5)

ttk.Button(root, text="Dersleri Getir", command=fetch_courses).pack(pady=10)

listbox = tk.Listbox(root, width=400, height=300)
listbox.pack(pady=10)

root.mainloop()