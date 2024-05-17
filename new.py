from tkinter import *  #Импортировать все модули из библиотеки Tkinter
from tkinter import ttk #Набор более современных тем
import json #Импортировать модуль json

global my_data_list #Хранение данных 
global currentRowIndex #Отслеживание индекса строки

my_data_list = [] # Пустой список для хранения 

primary = Tk() #Окно при вызове
primary.geometry("650x500") #Размер окна
primary.title('Учет учеников')# Заголовок окна

#новая запись
def make_new_record():     #Функция, которая вызывается при нажатии основной кнопки
    blankTuple = ('', '', '', '') #Кортеж из пустых строк
    open_popup('add', blankTuple, primary) #Функция с параметрами

#создание кнопки "добавить/удалить ученика"
btnNewRecord = Button(primary, text="Добавить/удалить ученика", bg="#7fffd4",font=("Calibri",10),      #параметры
                      padx=2, pady=4, command=lambda: make_new_record())
btnNewRecord.grid(row=0, column=0, sticky="w") #Размещение кнопки

#ttk.Treeview отвечает за отображение данных в виде таблицы
trv = ttk.Treeview(primary, columns=(1, 2, 3, 4, 5), show="headings", height="100")
trv.grid(row=1, column=0, rowspan=16, columnspan=5)

#функция сортировки столбцов
def sort(col, reverse): #Создание списка кортежей
    my_list = [(int(trv.set(k, col)) if col == 2 else trv.set(k, col), k) for k in trv.get_children("")]
    my_list.sort(reverse=reverse) #Сортировка списка кортежей
    for index, (_, k) in enumerate(my_list):
        trv.move(k, "", index) #Перемещение строки с идентификатором `k` на позицию `index` в таблице
    trv.heading(col, command=lambda: sort(col, not reverse)) #Вызов функция сортировки с противоположным направлением.

#название колонок и положеие названия в ячейке 
trv.heading(1, text="Действие", anchor="w", command=lambda: sort(1, False))  
trv.heading(2, text="Школа", anchor="center", command=lambda: sort(2, False))
trv.heading(3, text="Профиль", anchor="center", command=lambda: sort(3, False))
trv.heading(4, text="Год", anchor="center", command=lambda: sort(4, False))
trv.heading(5, text="ФИО", anchor="center", command=lambda: sort(5, False))

#положение и ширина колонок
trv.column("#1", anchor="w", width=100, stretch=True)      #w-положение слева
trv.column("#2", anchor="center", width=100, stretch=True)
trv.column("#3", anchor="center", width=140, stretch=False)
trv.column("#4", anchor="center", width=60, stretch=False) #stretch=True: должен ли столбец растягиваться по ширине виджета Treeview. 
trv.column("#5", anchor="w", width=250, stretch=False)

#Создание окна поиска
search_frame = Frame(primary, bg="#7fffd4", borderwidth=2, relief="raised")
search_frame.grid(row=0, column=1, sticky="e", padx=25, pady=15)

search_label = Label(search_frame, text="Поиск:", bg="#7fffd4", font=('Calibri', 10)) #LAbel -текстовая метка без возможности редактирования
search_label.grid(row=0, column=0, padx=5, pady=5) #Grid для размещения надписи внутри фрейма

#Окно для ввода 
search_entry = Entry(search_frame, width=25, font=('Calibri', 10)) #Окно для ввода тектса
search_entry.grid(row=0, column=1, padx=5, pady=5) #Поле ввода внутри

#Скроллбар
primary.grid_columnconfigure(1, weight=1) #Настраиваем растягиваемость
primary.grid_rowconfigure(1, weight=1)#Растягиваемость первой строки основного окна
scrollbar = Scrollbar(primary, orient='vertical', command=trv.yview) #Создается объект `Scrollbar`
scrollbar.grid(row=1, column=4, sticky='ns') #Размещение скроллбара в основном окне.
trv.config(yscrollcommand= scrollbar.set) #Установка вертикальной прокрутки

#Функция обновления данных
def update(data):
    remove_all_data_from_trv() #Очистка содержимого

    #Приравнивание кнопок к столбцам
    for key in data:
            school = key["school"]
            profile = key["profile"]
            year = key["year"]
            name = key["name"]

            trv.insert('', index='end', iid=rowIndex, text="",
                    values=('edit', school, profile, year, name)) # edit-значение в первом столбце, остальное атрибуты
            rowIndex = rowIndex + 1 #Увеличивается значение переменной rowIndex, использующаяся для определения следующего индекса строки

#Определение функции search_data,поиск в данных таблицы
def search_data():
    keyword = search_entry.get().lower() #Получение текста из поля ввода
    if keyword: #Проверка запроса
        remove_all_data_from_trv() #Очистка содержимого ttk.Treeview
        for index, key in enumerate(my_data_list): #Итерация по данным
            if keyword in key["school"].lower() or keyword in key["profile"].lower() \
                    or keyword in key["year"].lower() or keyword in key["name"].lower():
                trv.insert('', index='end', iid=index, text="",
                           values=('edit', key["school"], key["profile"], key["year"], key["name"]))

#Определение функции check,обработка событий клавиш
def check(e):
    typed = search_entry.get() 	
    if typed == '':
        load_trv_with_json()
    else:
        search_data()

# Create a binding on the entry box
search_entry.bind("<KeyRelease>", check)

#Чтение файла JSON и инициализирует переменную `my_data_list`
def load_json_from_file():     
    global my_data_list #Объявление переменной `my_data_list` как глобальной
    try:
        with open("data.json", "r", encoding="utf-8") as file_handler:
            my_data_list = json.load(file_handler) #Загрузка данных из файла JSON
        file_handler.close
        #print('file has been read and closed')
#Обработка случая, когда файл не найден.
    except FileNotFoundError:
        print("Файл 'data.json' не найден. Инициализация пустого списка.")
        my_data_list = []
    except Exception as e:
        # Обрабатываем другие исключения
        print(f"Произошла ошибка при загрузке данных: {e}")

#Определение функции, которая удаляет все данные из ttk.Treeview
def remove_all_data_from_trv():
    for item in trv.get_children():
        trv.delete(item)

#Определение функции, которая загружает данные из my_data_list в ttk.Treeview
def load_trv_with_json():
    global my_data_list

    remove_all_data_from_trv() #Вызов функции, которая очищает содержимое ttk.Treeview

    rowIndex = 1

#Итерация по данным в my_data_list    
    for key in my_data_list:
        school = key["school"]
        profile = key["profile"]
        year = key["year"]
        name = key["name"]

        trv.insert('', index='end', iid=rowIndex, text="",
                   values=('edit', school, profile, year, name))
        rowIndex = rowIndex + 1


#Определение функции, которая будет вызвана при отпускании кнопки мыши
def MouseButtonUpCallBack(event):
    global trv
    currentRowIndex = trv.selection()[0]
    lastTuple = (trv.item(currentRowIndex, 'values'))
    open_popup('edit', lastTuple, primary)

#Функция дочернего окна
def open_popup(_mode, _tuple, primary):
    child = Toplevel(primary)
    child.geometry("830x230")
    child.title('Ученик')
    child.grab_set()  

    child.configure(bg='LightBlue') #Установка фона дочернего окна
    load_form = True #Инициализация переменной 
    input_frame = LabelFrame(child, text='Введите данные ученика', bg="lightblue", font=('Calibri', 14), pady=2) #Создание рамки для ввода данных ученика

    input_frame.grid(row=0, rowspan=6, column=0, padx=10) #Размещение рамки в дочернем окне в первой строке
    #Создание 4 меток для каждого атрибута ученика 
    l1 = Label(input_frame, text="Школа", width=25, height=1, anchor="center", relief="ridge", font=('Calibri', 14))
    l2 = Label(input_frame, text="Профиль", width=25,height=1, anchor="center", relief="ridge", font=('Calibri', 14))
    l3 = Label(input_frame, text="Год", width=25, height=1, anchor="center", relief="ridge", font=('Calibri', 14))
    l4 = Label(input_frame, text="ФИО", width=25, height=1, anchor="center", relief="ridge", font=('Calibri', 14))
    #Размещение меток внутри рамки в соответствующих позициях
    l1.grid(column=0, row=0, padx=1, pady=4)
    l2.grid(column=0, row=1, padx=1, pady=4)
    l3.grid(column=0, row=2, padx=1, pady=4)
    l4.grid(column=0, row=3, padx=1, pady=4)
#Создание 4 полей для ввода данных для каждого атрибута ученика.Размещение полей ввода внутри рамки в соответств.позициях
    crm_school = Entry(input_frame, width=30, borderwidth=2, fg="black", font=('Calibri', 14))
    crm_school.grid(row=0, column=1)

    crm_profile = Entry(input_frame, width=30, borderwidth=2, fg="black", font=('Calibri', 14))
    crm_profile.grid(row=1, column=1)

    crm_year = Entry(input_frame, width=30, borderwidth=2, fg="black", font=('Calibri', 14))
    crm_year.grid(row=2, column=1)

    crm_name = Entry(input_frame, width=30, borderwidth=2, fg="black", font=('Calibri', 14))
    crm_name.grid(row=3, column=1)
#Создание кнопок 
    button_add = Button(input_frame, text="Добавить", padx=5, pady=10, bg="#C3F891", command=lambda: determineAction())
    button_add.grid(row=4, column=3, padx=3)

    button_delete = Button(input_frame, text="Удалить", padx=5, pady=10, bg="#FCABB2", command=lambda: delete_record())
    button_delete.grid(row=4, column=4, padx=10)

    button_cancel = Button(input_frame, text="Отменить", padx=5, pady=10, command=lambda: child_cancel())
    button_cancel.grid(row=4, column=5, padx=5)

    load_form = False 
    
    #функция удаления записи
    def delete_record():
        school = crm_school.get()
        profile = crm_profile.get()
        year = crm_year.get()
        name = crm_name.get() #получение значений из полей ввода
        process_request('_DELETE_', school, profile, year, name) #вызов функции для выполнение запроса на удаление записи
        reload_main_form () #обновление основной формы,вызывая функцию
        child.grab_release() #освобождение захвата ввода,позволяя взаимодействовать с основным окном 
        child.destroy() #закрытие дочернего окна
        child.update() #обновление дочернего окна
    
    def child_cancel():# Функция,которая отвечает за отмену действий
        child.grab_release() #освобождение захвата ввода
        child.destroy()
        child.update()

    def reload_main_form(): #Функция обновляет основную форму
        load_trv_with_json()

    def change_background_color(new_color): #функция изменения цвета фона для полей ввода
        crm_school.config(bg=new_color)
        crm_profile.config(bg=new_color)
        crm_year.config(bg=new_color)
        crm_name.config(bg=new_color)

    def add_entry(): #функция добавления данных
        school = crm_school.get()
        profile = crm_profile.get()
        year = crm_year.get()
        name = crm_name.get() #получение значений из полей ввода
#Если поле имени пустое,устанавливается красный цвет
        if len(name) == 0: 
            change_background_color("#FFB2AE")
            return

        process_request('_INSERT_', school, profile, year, name) #Вызов функции для выполнения запроса для записи

    def update_entry(): #функция обновления данных
        school = crm_school.get()
        profile = crm_profile.get()
        year = crm_year.get()
        name = crm_name.get()

        if len(name) == 0:
            change_background_color("#FFB2AE")
            return

        process_request('_UPDATE_', school, profile, year, name)

    def load_edit_field_with_row_data(_tuple):
        if len(_tuple) == 0: #Если переданный кортеж пуст, функция завершает выполнение.
            return

        crm_school.delete(0, END)
        crm_school.insert(0, _tuple[1])
        crm_profile.delete(0, END)
        crm_profile.insert(0, _tuple[2])
        crm_year.delete(0, END)
        crm_year.insert(0, _tuple[3])
        crm_name.delete(0, END)
        crm_name.insert(0, _tuple[4])

    if _mode == 'edit':
        load_edit_field_with_row_data(_tuple)

    def process_request(command_type, school, profile, year, name):
        global my_data_list
        global dirty

        dirty = True #Устанавливает флаг dirty в True. Этот флаг вероятно используется для отслеживания, были ли внесены изменения в данные.

        if command_type == "_UPDATE_":
            row = find_row_in_my_data_list(school)
            if row >= 0:
                dict = {"school": school, "profile": profile,
                        "year": year, "name": name}
                my_data_list[row] = dict

        elif command_type == "_INSERT_":
            dict = {"school": school, "profile": profile,
                        "year": year, "name": name}
            my_data_list.append(dict)

        elif command_type == "_DELETE_":
            row = find_row_in_my_data_list(school)
            if row >= 0:
                del my_data_list[row]

        save_json_to_file()
        clear_all_fields()

    #Функция ищет индекс строки, где значение совпадает с переданным значением.
    def find_row_in_my_data_list(school):
        global my_data_list
        row = 0
        found = False


        for rec in my_data_list:
            if rec["school"] == school:
                found = True
                break
            row = row + 1

        if (found == True):
            return (row)

        return (-1)
#Функция определения действий.
    def determineAction():
        if load_form == False:
            if _mode == "edit":
                update_entry()
            else:
                add_entry() #После того, как переменная load_form установлена в False: Если _mode равен "edit", вызывается update_entry().В противном случае вызывается add_entry().

        reload_main_form() #Вызывается reload_main_form() для обновления основной формы, после чего происходит освобождение захвата ввода, закрытие и обновление дочернего окна.
        child.grab_release()
        child.destroy()
        child.update()
#Функция сохраняет данные из my_data_list в файл "data.json" в удобочитаемом формате JSON.
    def save_json_to_file():
        global my_data_list
        with open("data.json", "w") as file_handler:
            json.dump(my_data_list, file_handler, indent=4)
        file_handler.close
        print('file has been written to and closed')

#Функция очищения данных.
    def clear_all_fields():
        crm_school.delete(0, END)
        crm_profile.delete(0, END)
        crm_year.delete(0, END)
        crm_name.delete(0, END)
        crm_name.focus_set()
        change_background_color("#FFFFFF")   


trv.bind("<ButtonRelease>", MouseButtonUpCallBack)
load_json_from_file()
load_trv_with_json()
primary.mainloop()
#Привязывает событие <ButtonRelease> к функции MouseButtonUpCallBack. Затем загружает данные из файла JSON с помощью load_json_from_file() 
#и обновляет основную форму с помощью load_trv_with_json(). Наконец, запускает основной цикл событий с primary.mainloop().
