import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def extract_courses(selected_department, selected_course_type):

    courses = set()
    excel_path = r"C:\Users\user\OneDrive\Masaüstü\coursecheckerPY\dersler.xlsx"
    df = pd.read_excel(excel_path)

    if selected_course_type != "HEPSİ":
        for index, row in df.iterrows():
            if selected_course_type in str(row['DERS']):#-----------------------------------------------!
                course_code = str(row['DERS']).strip()
                if(course_code[3] != " "):
                    course_code = course_code[:3] + " " + course_code[3:]
                course_code = course_code.upper()

                if row[selected_department] == 'X': #-----------------------------------------------!
                    courses.add(course_code)
    
    else:
        for index, row in df.iterrows():
            course_code = str(row['DERS']).strip()
            if(course_code[3] != " "):
                course_code = course_code[:3] + " " + course_code[3:]
            course_code = course_code.upper()

            if row[selected_department] == 'X': #-----------------------------------------------!
                courses.add(course_code)
    
    return courses

def get_courses_from_web(selected_course_type):
    url = "https://www.cankaya.edu.tr/dersler/"
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    time.sleep(2)
    
    courses = set()
    try:
        dropdown = driver.find_element(By.NAME, "DersCode")
        if selected_course_type != "HEPSİ":
            dropdown.send_keys(selected_course_type)
        else:
            dropdown.send_keys("Hepsi")
        dropdown.send_keys(Keys.RETURN)
        time.sleep(3)
        
        if selected_course_type != "HEPSİ":
            table_rows = driver.find_elements(By.XPATH, "//tr[@role='row']")
            for row in table_rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                
                if cols and selected_course_type in cols[0].text: #-----------------------------------------------!
                    
                    course_code = cols[0].text.replace("\u00a0", "").strip().upper()  # Özel boşluk karakterlerini düzelt ve normalleştir
                    courses.add(course_code)
        
        if selected_course_type == "HEPSİ":
            visited_pages = set()

            while True:
                current_page = driver.find_element(By.CLASS_NAME, "paginate_button.current").text
                if current_page in visited_pages:
                    break
                visited_pages.add(current_page)
                
                table_rows = driver.find_elements(By.XPATH, "//tr[@role='row']")
                for row in table_rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if cols:
                        course_code = cols[0].text.replace("\u00a0", "").strip().upper()
                        courses.add(course_code)
                
                next_buttons = driver.find_elements(By.CLASS_NAME, "paginate_button")
                next_button_clicked = False
                for btn in next_buttons:
                    if btn.text.isdigit() and btn.text not in visited_pages:
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(2)
                        next_button_clicked = True
                        break
                
                if not next_button_clicked:
                    break
        
        driver.quit()
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
    
    courses = extract_courses(selected_department, selected_course_type).intersection(get_courses_from_web(selected_course_type))
    sorted_courses = sorted(courses)  # Alfabetik sıralama burada yapılıyor
    
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
department_dropdown['values'] = ("CENG", "EE", "ECE","IE","CE","ME","MSE","MECE","SENG")
department_dropdown.pack(pady=5)

ttk.Label(root, text="Ders Tipi Seçiniz:").pack(pady=5)
course_type_var = tk.StringVar()
course_type_dropdown = ttk.Combobox(root, textvariable=course_type_var)
course_type_dropdown['values'] = ("HEPSİ", "CEC", "MAN", "THEA", "INTT", "ECON", "ALM", "BAF", "ELL", "ENG", "FRAN", "ITAL", "RUS", "SPAN", "LAW", "MATH", "MCS", "MIS", "OTT", "PES", "PHIL", "PHYS", "PSI", "SOC", "TINS" )
course_type_dropdown.pack(pady=5)

ttk.Button(root, text="Dersleri Getir", command=fetch_courses).pack(pady=10)

listbox = tk.Listbox(root, width=400, height=300)
listbox.pack(pady=10)

root.mainloop()